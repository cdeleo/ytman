import videos_api

import dpy
import endpoints
import mock
import unittest
import webtest

from google.appengine.ext import testbed

import thumbnails
import videos

dpy.SetTestMode()

class VideosApiTest(unittest.TestCase):

  API_PREFIX = '/_ah/api/videos/v1'

  USER_ID = 'test@example.com'
  VIDEO_ID = 'fake_video_id'

  BG_KEY = 'fake_bg_key'
  TITLE = 'fake_title'
  SUBTITLE = 'fake_subtitle'

  DESCRIPTION = 'fake_description'
  THUMBNAIL_DATA = 'fake_thumbnail_data'

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

    endpoints.get_current_user = mock.Mock()
    endpoints.get_current_user().user_id.return_value = self.USER_ID

    self.thumbnails_client = mock.Mock(thumbnails.ThumbnailsClient)
    self.thumbnails_client.get.return_value = self.THUMBNAIL_DATA
    self.videos_client = mock.Mock(videos.VideosClient)

    @endpoints.api(name='videos', version='v1')
    class _TestVideosApi(videos_api.VideosApi):

      def __init__(inner_self):
        super(_TestVideosApi, inner_self).__init__(
            thumbnails_client=self.thumbnails_client,
            videos_client=self.videos_client)

    self.app = webtest.TestApp(endpoints.api_server([_TestVideosApi]))

  def tearDown(self):
    self.testbed.deactivate()

  def test_publish(self):
    req = {
      'video_id': self.VIDEO_ID,
      'bg_key': self.BG_KEY,
      'title': self.TITLE,
      'subtitle': self.SUBTITLE,
      'description': self.DESCRIPTION,
    }
    resp = self.app.post_json(self.API_PREFIX + '/publish', req)
    self.assertEqual(self.get_status_code(resp), 200)
    self.thumbnails_client.get.assert_called_with(
        self.BG_KEY, self.TITLE, self.SUBTITLE)
    self.videos_client.set_thumbnail.assert_called_with(
        self.VIDEO_ID, self.THUMBNAIL_DATA)
    self.videos_client.set_metadata.assert_called_with(
        self.VIDEO_ID, self.TITLE, self.SUBTITLE,
        description=self.DESCRIPTION, publish_status='private')

  # Utility functions

  def get_status_code(self, resp):
    if isinstance(resp.status, basestring):
      return int(resp.status.split(' ')[0])
    else:
      return int(resp.status)

if __name__ == '__main__':
    unittest.main()
