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

class User(ndb.Model):
  pass

class Image(ndb.Model):
  name = ndb.StringProperty()
  url = ndb.StringProperty(indexed=False)
  metadata = ndb.JsonProperty()

  @classmethod
  def get_user_id_from_key(cls, key):
    if len(key.pairs()) != 2 or key.pairs()[0][0] != User.__name__:
      return None
    return key.pairs()[0][1]

  @classmethod
  def get_index_name(cls, user_id):
    return 'images/%s' % user_id

  INDEX_FIELD_NAME_PREFIXES = 'name_prefixes'

  def _post_put_hook(self, future):
    if future.get_exception() is not None:
      return
    index_name = self.get_index_name(self.get_user_id_from_key(self.key))
    search.Index(index_name).put(
        search.Document(
            doc_id=self.key.urlsafe(),
            fields=[
                search.TextField(
                    name=Image.INDEX_FIELD_NAME_PREFIXES,
                    value=','.join(_get_prefixes(self.name)))]))

  @classmethod
  def _post_delete_hook(cls, key, future):
    if future.get_exception() is not None:
      return
    index_name = cls.get_index_name(cls.get_user_id_from_key(key))
    search.Index(index_name).delete(key.urlsafe())

class _GcsImageWriter(object):

  def write(self, key, data):
    filename = '/%s/images/%s/%s.png' % (
        app_identity.get_default_gcs_bucket_name(),
        Image.get_user_id_from_key(ndb.Key(urlsafe=key)),
        key)
    gcs_file = gcs.open(
        filename,
        'w',
        content_type='image/png',
        retry_params=gcs.RetryParams(backoff_factor=1.1))
    gcs_file.write(data)
    gcs_file.close()
    return images.get_serving_url(None, filename=('/gs' + filename))

class CrossUserError(Exception):
  pass

class ImagesClient(object):

  def __init__(self, writer=None, default_page_size=10):
    self._writer = writer if writer else _GcsImageWriter()
    self._default_page_size = default_page_size

  def list(self, user_id, token=None, page_size=None):
    if page_size is None:
      page_size = self._default_page_size
    fetch_args = {'page_size': page_size}
    if token:
      fetch_args['start_cursor'] = ndb.Cursor.from_websafe_string(token)
    results, cursor, more = (
        Image
            .query(ancestor=ndb.Key(User, user_id))
            .order(Image.name)
            .fetch_page(**fetch_args))
    return results, cursor.to_websafe_string() if cursor and more else None

  def search(self, user_id, query, page_size=None):
    if not query:
      return []
    if page_size is None:
      page_size = self._default_page_size
    query_string = '%s: %s' % (Image.INDEX_FIELD_NAME_PREFIXES, query)
    query_obj = search.Query(
        query_string=query_string,
        options=search.QueryOptions(limit=page_size, ids_only=True))
    docs = search.Index(Image.get_index_name(user_id)).search(query_obj)
    return ndb.get_multi([self.parse_key(doc.doc_id) for doc in docs])

  def create(self, user_id, name, data, metadata):
    key = ndb.Key(User, user_id, Image, Image.allocate_ids(1)[0])
    image = Image(key=key, name=name, metadata=metadata)
    image.url = self._writer.write(key.urlsafe(), data)
    image.put()
    return image

  def _check_cross_user(self, user_id, key):
    key_user_id = Image.get_user_id_from_key(key)
    if user_id != key_user_id:
      raise CrossUserError(
          'Expected user %s, found %s' % (user_id, key_user_id))

  def update(self, user_id, key, delta, mask):
    self._check_cross_user(user_id, key)
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

  def delete(self, user_id, key):
    self._check_cross_user(user_id, key)
    key.delete()

  @staticmethod
  def parse_key(key):
    return ndb.Key(urlsafe=key)
