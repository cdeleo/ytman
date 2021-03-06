import images_api

import dpy
import endpoints
import mock
import unittest
import webtest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

import images
import models

dpy.SetTestMode()

class ImagesApiTest(unittest.TestCase):

  API_PREFIX = '/_ah/api/images/v1'
  TEST_IMAGE = models.Image(
      key=ndb.Key(models.Image, 'fake_key'),
      name='test image',
      url='test_url',
      metadata={'test_arg': 'test_value'})
  TEST_IMAGE_JSON = {
      'key': TEST_IMAGE.key.urlsafe(),
      'name': TEST_IMAGE.name,
      'url': TEST_IMAGE.url,
      'metadata': [{'key': 'test_arg', 'value': 'test_value'}]}
  IMAGE_DATA = 'data:image/png;base64,b2N0b3B1cw=='  # 'octopus' in urlsafe b64
  IMAGE_DATA_DECODED = 'octopus'
  USER_ID = 'test@example.com'

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

    endpoints.get_current_user = mock.Mock()
    endpoints.get_current_user().user_id.return_value = self.USER_ID

    self.client = mock.Mock(images.ImagesClient)
    self.client.parse_key = images.ImagesClient.parse_key

    @endpoints.api(name='images', version='v1')
    class _TestImagesApi(images_api.ImagesApi):

      def __init__(inner_self):
        super(_TestImagesApi, inner_self).__init__(images_client=self.client)

    self.app = webtest.TestApp(endpoints.api_server([_TestImagesApi]))

  def tearDown(self):
    self.testbed.deactivate()

  # Tests

  def test_list(self):
    self.client.list.return_value = [self.TEST_IMAGE], None
    resp = self.app.get(self.API_PREFIX + '/list')
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'images': [self.TEST_IMAGE_JSON]})
    self.client.list.assert_called_with()

  def test_list_continue(self):
    self.client.list.return_value = [self.TEST_IMAGE], 'test_token_1'
    resp = self.app.get(self.API_PREFIX + '/list?token=test_token_0')
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(
        resp.json, {'images': [self.TEST_IMAGE_JSON], 'token': 'test_token_1'})
    self.client.list.assert_called_with(token='test_token_0')

  def test_list_page_size(self):
    self.client.list.return_value = [self.TEST_IMAGE], None
    resp = self.app.get(self.API_PREFIX + '/list?page_size=20')
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'images': [self.TEST_IMAGE_JSON]})
    self.client.list.assert_called_with(page_size=20)

  def test_search(self):
    self.client.search.return_value = [self.TEST_IMAGE]
    resp = self.app.get(self.API_PREFIX + '/search?q=ima')
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'images': [self.TEST_IMAGE_JSON]})
    self.client.search.assert_called_with('ima')

  def test_search_page_size(self):
    self.client.search.return_value = [self.TEST_IMAGE]
    resp = self.app.get(self.API_PREFIX + '/search?q=ima&page_size=20')
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'images': [self.TEST_IMAGE_JSON]})
    self.client.search.assert_called_with('ima', page_size=20)

  def test_create(self):
    self.client.create.return_value = self.TEST_IMAGE
    resp = self.app.post_json(
        self.API_PREFIX + '/create',
        {'name': self.TEST_IMAGE_JSON['name'],
         'data': self.IMAGE_DATA,
         'metadata': self.TEST_IMAGE_JSON['metadata']})
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'image': self.TEST_IMAGE_JSON})
    self.client.create.assert_called_with(
        self.TEST_IMAGE.name,
        self.IMAGE_DATA_DECODED,
        self.TEST_IMAGE.metadata)

  def test_update(self):
    self.client.update.return_value = self.TEST_IMAGE
    resp = self.app.put_json(
        self.API_PREFIX + '/' + self.TEST_IMAGE_JSON['key'],
        {'delta': self.TEST_IMAGE_JSON, 'mask': ['metadata']})
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertEqual(resp.json, {'image': self.TEST_IMAGE_JSON})
    self.client.update.assert_called_with(
        self.TEST_IMAGE.key,
        models.Image(
            name = self.TEST_IMAGE.name,
            metadata = self.TEST_IMAGE.metadata),
        ['metadata'])

  def test_delete(self):
    resp = self.app.delete(self.API_PREFIX + '/' + self.TEST_IMAGE_JSON['key'])
    self.assertEqual(self.get_status_code(resp), 200)
    self.client.delete.assert_called_with(self.TEST_IMAGE.key)

  # Utility functions

  def get_status_code(self, resp):
    if isinstance(resp.status, basestring):
      return int(resp.status.split(' ')[0])
    else:
      return int(resp.status)

if __name__ == '__main__':
    unittest.main()
