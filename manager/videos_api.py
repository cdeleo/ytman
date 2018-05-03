import dpy
import endpoints

from protorpc import messages
from protorpc import remote

import auth
import thumbnails
import video_queue
import videos

class PublishRequest(messages.Message):
  video_id = messages.StringField(1)
  bg_key = messages.StringField(2)
  title = messages.StringField(3)
  subtitle = messages.StringField(4)
  description = messages.StringField(5)

  class PublishMode(messages.Enum):
    NONE = 1
    NOW = 2
    ENQUEUE = 3
    PREEMPT = 4
  publish_mode = messages.EnumField(PublishMode, 6, default=PublishMode.NONE)

class PublishResponse(messages.Message):
  pass

@dpy.Inject
class VideosApi(remote.Service):

  def __init__(
      self,
      thumbnails_client=dpy.IN,
      videos_client=dpy.IN,
      video_queue_client=dpy.IN):
    self._thumbnails_client = thumbnails_client
    self._videos_client = videos_client
    self._video_queue_client = video_queue_client

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

    video_name = self._videos_client.get_video_name(req.title, req.subtitle)
    publish_status = (
        self._videos_client.PUBLIC
        if req.publish_mode == PublishRequest.PublishMode.NOW
        else self._videos_client.PRIVATE)
    self._videos_client.set_metadata(
        req.video_id, video_name,
        description=req.description, publish_status=publish_status)

    video = video_queue.Video(id=req.video_id, name=video_name)
    if req.publish_mode == PublishRequest.PublishMode.ENQUEUE:
      self._video_queue_client.push(video)
    elif req.publish_mode == PublishRequest.PublishMode.PREEMPT:
      self._video_queue_client.insert_front(video)

    return PublishResponse()
