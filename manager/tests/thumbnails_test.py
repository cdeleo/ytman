import thumbnails

import dpy
import mock
import unittest

dpy.SetTestMode()

class ThumbnailsTest(unittest.TestCase):

  BG_KEY = 'fake_bg_key'
  TITLE = 'fake_title'
  SUBTITLE = 'fake_subtitle'
  IMAGE_DATA = 'b2N0b3B1cw'  # 'octopus' in urlsafe b64, no padding

  def setUp(self):
    self.service = mock.Mock()
    self.service.get().execute.return_value = {
      'image_data': self.IMAGE_DATA,
    }
    self.client = thumbnails.ThumbnailsClient(thumbnails_service=self.service)

  def test_get(self):
    self.assertEqual(
        self.client.get(self.BG_KEY, self.TITLE, self.SUBTITLE), 'octopus')
    expected_request = {
      'bg_key': self.BG_KEY,
      'title': self.TITLE,
      'subtitle': self.SUBTITLE,
    }
    self.service.get.assert_called_with(expected_request)
