import images

import endpoints
import unittest
import webtest

from google.appengine.ext import testbed

class ImagesApiTest(unittest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.setup_env(current_version_id='testbed.version')
    self.testbed.activate()
    self.testbed.init_all_stubs()

    self.app = webtest.TestApp(
        endpoints.api_server([images.ImagesApi], restricted=False))

  def tearDown(self):
    self.testbed.deactivate()

  def test_list(self):
    pass

if __name__ == '__main__':
    unittest.main()
