import endpoints
import os

from protorpc import messages
from protorpc import remote

class PublishRequest(messages.Message):
  video_id = messages.StringField(1)
  bg_key = messages.StringField(2)
  title = messages.StringField(3)
  subtitle = messages.StringField(4)
  description = messages.StringField(5)

class PublishResponse(messages.Message):
  pass

class VideosApi(remote.Service):

  TOKEN_PREFIX = 'Bearer '

  def _get_credentials(self):
    token = os.environ['HTTP_AUTHORIZATION']
    if token.startswith(self.TOKEN_PREFIX):
      token = token[len(self.TOKEN_PREFIX):]
    return oauth2client.client.AccessTokenCredentials(token, 'ytman')

  @endpoints.method(
      PublishRequest,
      PublishResponse,
      path='publish',
      http_method='POST',
      name='publish')
  def publish_handler(self, req):
    return PublishResponse()
