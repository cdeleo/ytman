import cloudstorage as gcs
import dpy

from google.appengine.api import app_identity
from google.appengine.api import images
from google.appengine.api import search
from google.appengine.ext import ndb

import models

@dpy.Injectable.named('image_writer')
class _GcsImageWriter(object):

  def __init__(self):
    pass

  def write(self, key, data):
    filename = '/%s/images/%s/%s.png' % (
        app_identity.get_default_gcs_bucket_name(),
        models.Image.get_user_id_from_key(ndb.Key(urlsafe=key)),
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

@dpy.Injectable.named('images_client')
class ImagesClient(object):

  _DEFAULT_PAGE_SIZE = 10

  def __init__(self, image_writer=dpy.IN):
    self._writer = image_writer
    self._default_page_size = self._DEFAULT_PAGE_SIZE

  def set_default_page_size(self, default_page_size):
    self._default_page_size = default_page_size

  @dpy.Inject
  def list(self, token=None, page_size=None, user_id=dpy.IN):
    if page_size is None:
      page_size = self._default_page_size
    fetch_args = {'page_size': page_size}
    if token:
      fetch_args['start_cursor'] = ndb.Cursor.from_websafe_string(token)
    results, cursor, more = (
        models.Image
            .query(ancestor=ndb.Key(models.User, user_id))
            .order(models.Image.name)
            .fetch_page(**fetch_args))
    return results, cursor.to_websafe_string() if cursor and more else None

  @dpy.Inject
  def search(self, query, page_size=None, user_id=dpy.IN):
    if not query:
      return []
    if page_size is None:
      page_size = self._default_page_size
    query_string = '%s: %s' % (models.Image.INDEX_FIELD_NAME_PREFIXES, query)
    query_obj = search.Query(
        query_string=query_string,
        options=search.QueryOptions(limit=page_size, ids_only=True))
    docs = search.Index(models.Image.get_index_name(user_id)).search(query_obj)
    return ndb.get_multi([self.parse_key(doc.doc_id) for doc in docs])

  @dpy.Inject
  def create(self, name, data, metadata, user_id=dpy.IN):
    key = ndb.Key(
        models.User, user_id, models.Image, models.Image.allocate_ids(1)[0])
    image = models.Image(key=key, name=name, metadata=metadata)
    image.url = self._writer.write(key.urlsafe(), data)
    image.put()
    return image

  def _check_cross_user(self, user_id, key):
    key_user_id = models.Image.get_user_id_from_key(key)
    if user_id != key_user_id:
      raise CrossUserError(
          'Expected user %s, found %s' % (user_id, key_user_id))

  @dpy.Inject
  def update(self, key, delta, mask, user_id=dpy.IN):
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

  @dpy.Inject
  def delete(self, key, user_id=dpy.IN):
    self._check_cross_user(user_id, key)
    key.delete()

  @staticmethod
  def parse_key(key):
    return ndb.Key(urlsafe=key)
