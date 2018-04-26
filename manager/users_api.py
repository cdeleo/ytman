import endpoints
import os

from protorpc import messages
from protorpc import remote

class VerifyCredentialsRequest(messages.Message):
  pass

class VerifyCredentialsResponse(messages.Message):
  has_credentials = messages.BooleanField(1)

class ProvideCredentialsRequest(messages.Message):
  auth_code = messages.StringField(1)

class ProvideCredentialsResponse(messages.Message):
  pass

class UsersApi(remote.Service):

  @endpoints.method(
      VerifyCredentialsRequest,
      VerifyCredentialsResponse,
      path='credentials',
      http_method='GET',
      name='verify_credentials')
  def verify_credentials_handler(self, req):
    return VerifyCredentialsResponse()

  @endpoints.method(
      ProvideCredentialsRequest,
      ProvideCredentialsResponse,
      path='credentials',
      http_method='POST',
      name='provide_credentials')
  def provide_credentials_handler(self, req):
    return ProvideCredentialsResponse()
