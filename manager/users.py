import dpy

from google.appengine.ext import ndb
from oauth2client import client as oauth2client

import constants
import models

@dpy.Injectable.named('auth_code_exchanger')
class _OAuth2AuthCodeExchanger(object):

  def __init__(self):
    pass

  @dpy.Inject
  def exchange(
      self, client_secret, auth_code, client_id=dpy.IN, scopes=dpy.IN):
    return oauth2client.credentials_from_code(
        client_id, client_secret, scopes, auth_code)

@dpy.Injectable.named('users_client')
class UsersClient(object):

  def __init__(self, auth_code_exchanger=dpy.IN):
    self._exchanger = auth_code_exchanger
    self._client_secret = models.ClientSecret.get()

  @dpy.Inject
  def get_credentials(self, user_id=dpy.IN):
    user = ndb.Key(models.User, user_id).get()
    if user and user.credentials:
      return oauth2client.OAuth2Credentials.from_json(user.credentials)
    else:
      return None

  @dpy.Inject
  def set_credentials(self, credentials, user_id=dpy.IN):
    models.User(id=user_id, credentials=credentials.to_json()).put()

  def exchange_auth_code(self, auth_code):
    return self._exchanger.exchange(self._client_secret, auth_code)
