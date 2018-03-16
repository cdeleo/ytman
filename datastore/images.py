import cloudstorage as gcs

from google.appengine.api import app_identity
from google.appengine.api import images
from google.appengine.ext import ndb

class Image(ndb.Model):
  name = ndb.StringProperty()
  url = ndb.StringProperty(indexed=False)
  metadata = ndb.JsonProperty()

class _GcsImageWriter(object):

  def write(self, key, data):
    filename = '/%s/%s' % (app_identity.get_default_gcs_bucket_name(), key)
    gcs_file = gcs.open(
        filename,
        'w',
        content_type='image/png',
        retry_params=gcs.RetryParams(backoff_factor=1.1))
    gcs_file.write(data)
    gcs_file.close()
    return images.get_serving_url(filename=filename)

class ImageClient(object):

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
    return []

  def create(self, name, data, metadata):
    key = ndb.Key(Image, Image.allocate_ids(1)[0])
    image = Image(key=key, name=name, metadata=metadata)
    image.url = self._writer.write(key.urlsafe(), data)
    image.put()
    return key.urlsafe()

  def update(self, key, delta, mask):
    image = ndb.Key(urlsafe=key).get()
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
    ndb.Key(urlsafe=key).delete()
