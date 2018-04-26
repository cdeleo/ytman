from google.appengine.api import search
from google.appengine.ext import ndb

class User(ndb.Model):
  pass

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
