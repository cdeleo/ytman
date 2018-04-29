import dpy
import endpoints

from protorpc import messages
from protorpc import remote

import constants
import users

class VerifyCredentialsRequest(messages.Message):
  pass

class VerifyCredentialsResponse(messages.Message):
  has_credentials = messages.BooleanField(1)

class ProvideCredentialsRequest(messages.Message):
  auth_code = messages.StringField(1)

class ProvideCredentialsResponse(messages.Message):
  pass

@dpy.Inject
class UsersApi(remote.Service):

  def __init__(self, users_client=dpy.IN):
    self.client = users_client

  @classmethod
  def get_current_user_id(cls):
    user = endpoints.get_current_user()
    if not user:
      raise endpoints.UnauthorizedException
    return user.user_id()

  @endpoints.method(
      VerifyCredentialsRequest,
      VerifyCredentialsResponse,
      path='credentials',
      http_method='GET',
      name='verify_credentials')
  def verify_credentials_handler(self, req):
    credentials = self.client.get_credentials(self.get_current_user_id())
    return VerifyCredentialsResponse(has_credentials=credentials is not None)

  @endpoints.method(
      ProvideCredentialsRequest,
      ProvideCredentialsResponse,
      path='credentials',
      http_method='POST',
      name='provide_credentials')
  def provide_credentials_handler(self, req):
    credentials = self.client.exchange_auth_code(req.auth_code)
    self.client.set_credentials(self.get_current_user_id(), credentials)
    return ProvideCredentialsResponse()
