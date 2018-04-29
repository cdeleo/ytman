import auth
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

  @endpoints.method(
      VerifyCredentialsRequest,
      VerifyCredentialsResponse,
      path='credentials',
      http_method='GET',
      name='verify_credentials')
  @auth.require_auth
  def verify_credentials_handler(self, req):
    credentials = self.client.get_credentials()
    return VerifyCredentialsResponse(has_credentials=credentials is not None)

  @endpoints.method(
      ProvideCredentialsRequest,
      ProvideCredentialsResponse,
      path='credentials',
      http_method='POST',
      name='provide_credentials')
  @auth.require_auth
  def provide_credentials_handler(self, req):
    credentials = self.client.exchange_auth_code(req.auth_code)
    self.client.set_credentials(credentials)
    return ProvideCredentialsResponse()
