import dpy
import endpoints

from protorpc import message_types
from protorpc import messages
from protorpc import remote

import auth
import video_queue

class ListRequest(messages.Message):
  pass

class EnqueuedVideo(messages.Message):
  id = messages.StringField(1)
  name = messages.StringField(2)

class ListResponse(messages.Message):
  videos = messages.MessageField(EnqueuedVideo, 1, repeated=True)

DELETE_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    id=messages.StringField(1))

class DeleteResponse(messages.Message):
  pass

@dpy.Inject
class VideoQueueApi(remote.Service):

  def __init__(
      self,
      video_queue_client=dpy.IN):
    self._video_queue_client = video_queue_client

  @endpoints.method(
      ListRequest,
      ListResponse,
      path='list',
      http_method='GET',
      name='list')
  @auth.require_auth
  def list_handler(self, req):
    videos = [EnqueuedVideo(id=v.id, name=v.name)
              for v in self._video_queue_client.list()]
    return ListResponse(videos=videos)

  @endpoints.method(
      DELETE_RESOURCE,
      DeleteResponse,
      path='{id}',
      http_method='DELETE',
      name='delete')
  @auth.require_auth
  def delete_handler(self, req):
    self._video_queue_client.delete(req.id)
    return DeleteResponse()
