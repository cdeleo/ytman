import dpy
import endpoints

from protorpc import messages
from protorpc import remote

import auth
import thumbnails
import videos

class PublishRequest(messages.Message):
  video_id = messages.StringField(1)
  bg_key = messages.StringField(2)
  title = messages.StringField(3)
  subtitle = messages.StringField(4)
  description = messages.StringField(5)

class PublishResponse(messages.Message):
  pass

@dpy.Inject
class VideosApi(remote.Service):

  def __init__(self, thumbnails_client=dpy.IN, videos_client=dpy.IN):
    self._thumbnails_client = thumbnails_client
    self._videos_client = videos_client

  @endpoints.method(
      PublishRequest,
      PublishResponse,
      path='publish',
      http_method='POST',
      name='publish')
  @auth.require_auth
  def publish_handler(self, req):
    thumbnail_data = self._thumbnails_client.get(
        req.bg_key, req.title, req.subtitle)
    self._videos_client.set_thumbnail(req.video_id, thumbnail_data)
    return PublishResponse()
