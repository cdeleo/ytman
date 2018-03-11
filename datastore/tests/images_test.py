import images

import endpoints
import pdb
import unittest
import webtest

from google.appengine.ext import testbed

class ImagesApiTest(unittest.TestCase):

  API_PREFIX = '/_ah/api/images/v1'
  IMAGE_NAME = 'test image'
  IMAGE_DATA = 'test data'

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

    self.app = webtest.TestApp(endpoints.api_server([images.ImagesApi]))

  def tearDown(self):
    self.testbed.deactivate()

  # Tests

  def test_create(self):
    req = {'image': self.image(self.IMAGE_NAME, self.IMAGE_DATA)}
    resp = self.app.post_json(self.API_PREFIX + '/create', req)
    self.assertEqual(self.get_status_code(resp), 200)
    self.assertIn('id', resp.json)
    image_id = resp.json['id']
    self.assertEqual(
        self.list_images(),
        [self.image(self.IMAGE_NAME, self.IMAGE_DATA, image_id=image_id)])

  # Utility functions

  def image(self, name, data, image_id=None):
    image = {'name': name, 'data': data}
    if image_id is not None:
      image['id'] = image_id
    return image

  def get_status_code(self, resp):
    if isinstance(resp.status, basestring):
      return int(resp.status.split(' ')[0])
    else:
      return int(resp.status)

  def list_images(self):
    return self.app.get(self.API_PREFIX + '/list').json

if __name__ == '__main__':
    unittest.main()
