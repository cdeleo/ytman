from google.appengine.ext import ndb
from oauth2client import client as oauth2client

import models

class _OAuth2AuthCodeExchanger(object):

  def exchange(self, client_id, client_secret, scopes, auth_code):
    return oauth2client.credentials_from_code(
        client_id, client_secret, scopes, auth_code)

class UsersClient(object):

  def __init__(self, client_id, scopes, exchanger=None):
    self.client_id = client_id
    self.scopes = scopes
    self._exchanger = exchanger if exchanger else _OAuth2AuthCodeExchanger()

    self._client_secret = models.ClientSecret.get()

  def get_credentials(self, user_id):
    user = ndb.Key(models.User, user_id).get()
    if user and user.credentials:
      return oauth2client.OAuth2Credentials.from_json(user.credentials)
    else:
      return None

  def set_credentials(self, user_id, credentials):
    models.User(id=user_id, credentials=credentials.to_json()).put()

  def exchange_auth_code(self, auth_code):
    return self._exchanger.exchange(
        self.client_id, self._client_secret, self.scopes, auth_code)
