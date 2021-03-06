import users_api

import dpy
import endpoints
import mock
import unittest
import webtest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

import images
import models
import users

dpy.SetTestMode()

class UsersApiTest(unittest.TestCase):

  API_PREFIX = '/_ah/api/users/v1'
  USER_ID = 'test@example.com'
  AUTH_CODE = 'fake_auth_code'

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

    endpoints.get_current_user = mock.Mock()
    endpoints.get_current_user().user_id.return_value = self.USER_ID

    self.client = mock.Mock(users.UsersClient)

    @endpoints.api(name='users', version='v1')
    class _TestUsersApi(users_api.UsersApi):

      def __init__(inner_self):
        super(_TestUsersApi, inner_self).__init__(users_client=self.client)

    self.app = webtest.TestApp(endpoints.api_server([_TestUsersApi]))

  def tearDown(self):
    self.testbed.deactivate()

  # Tests
  def test_verify_credentials(self):
    resp = self.app.get(self.API_PREFIX + '/credentials')
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'has_credentials': True})
    self.client.get_credentials.assert_called_with()

  def test_verify_credentials_none(self):
    self.client.get_credentials.return_value = None
    resp = self.app.get(self.API_PREFIX + '/credentials')
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'has_credentials': False})
    self.client.get_credentials.assert_called_with()

  def test_provide_credentials(self):
    resp = self.app.post_json(
        self.API_PREFIX + '/credentials', {'auth_code': self.AUTH_CODE})
    self.client.exchange_auth_code.assert_called_with(self.AUTH_CODE)
    self.client.set_credentials.assert_called_with(
        self.client.exchange_auth_code())

  # Utility functions

  def get_status_code(self, resp):
    if isinstance(resp.status, basestring):
      return int(resp.status.split(' ')[0])
    else:
      return int(resp.status)
