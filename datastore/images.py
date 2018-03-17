import cloudstorage as gcs

from google.appengine.api import app_identity
from google.appengine.api import images
from google.appengine.api import search
from google.appengine.ext import ndb

def _get_prefixes(value):
  prefixes = set()
  for token in value.split():
    for i in xrange(1, len(token) + 1):
      prefixes.add(token[:i])
  return prefixes

class Image(ndb.Model):
  name = ndb.StringProperty()
  url = ndb.StringProperty(indexed=False)
  metadata = ndb.JsonProperty()

  INDEX_NAME = 'images'
  INDEX_FIELD_NAME_PREFIXES = 'name_prefixes'

  def _post_put_hook(self, future):
    if future.get_exception() is not None:
      return
    search.Index(Image.INDEX_NAME).put(
        search.Document(
            doc_id=self.key.urlsafe(),
            fields=[
                search.TextField(
                    name=Image.INDEX_FIELD_NAME_PREFIXES,
                    value=','.join(_get_prefixes(self.name)))]))

  @classmethod
  def _post_delete_hook(self, key, future):
    if future.get_exception() is not None:
      return
    search.Index(Image.INDEX_NAME).delete(key.urlsafe())

class _GcsImageWriter(object):

  def write(self, key, data):
    filename = '/%s/images/%s.png' % (
        app_identity.get_default_gcs_bucket_name(), key)
    gcs_file = gcs.open(
        filename,
        'w',
        content_type='image/png',
        retry_params=gcs.RetryParams(backoff_factor=1.1))
    gcs_file.write(data)
    gcs_file.close()
    return images.get_serving_url(None, filename=('/gs' + filename))

class ImagesClient(object):

  def __init__(self, writer=None, page_size=10):
    self._writer = writer if writer else _GcsImageWriter()
    self._page_size = page_size

  def list(self, token=None):
    fetch_args = {'page_size': self._page_size}
    if token:
      fetch_args['start_cursor'] = ndb.Cursor.from_websafe_string(token)
    results, cursor, more = (
        Image.query().order(Image.name).fetch_page(**fetch_args))
    return results, cursor.to_websafe_string() if cursor and more else None

  def search(self, query):
    query_string = '%s: %s' % (Image.INDEX_FIELD_NAME_PREFIXES, query)
    query_obj = search.Query(
        query_string=query_string,
        options=search.QueryOptions(limit=self._page_size, ids_only=True))
    docs = search.Index(Image.INDEX_NAME).search(query_obj)
    return ndb.get_multi([self.parse_key(doc.doc_id) for doc in docs])

  def create(self, name, data, metadata):
    key = ndb.Key(Image, Image.allocate_ids(1)[0])
    image = Image(key=key, name=name, metadata=metadata)
    image.url = self._writer.write(key.urlsafe(), data)
    image.put()
    return image

  def update(self, key, delta, mask):
    image = key.get()
    if 'name' in mask:
      image.name = delta.name
    if 'metadata' in mask:
      for k, v in delta.metadata.iteritems():
        if v is None:
          image.metadata.pop(k, None)
        else:
          image.metadata[k] = v
    image.put()
    return image

  def delete(self, key):
    key.delete()

  @staticmethod
  def parse_key(key):
    return ndb.Key(urlsafe=key)
