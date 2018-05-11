import video_queue_api

import dpy
import endpoints
import mock
import unittest
import webtest

from google.appengine.ext import testbed

import video_queue

dpy.SetTestMode()

class VideosApiTest(unittest.TestCase):

  API_PREFIX = '/_ah/api/video_queue/v1'

  USER_ID = 'test@example.com'
  VIDEO_ID = 'fake_video_id'

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

    endpoints.get_current_user = mock.Mock()
    endpoints.get_current_user().user_id.return_value = self.USER_ID

    self.video_queue_client = mock.Mock(video_queue.VideoQueueClient)

    @endpoints.api(name='video_queue', version='v1')
    class _TestVideoQueueApi(video_queue_api.VideoQueueApi):

      def __init__(inner_self):
        super(_TestVideoQueueApi, inner_self).__init__(
            video_queue_client=self.video_queue_client)

    self.app = webtest.TestApp(endpoints.api_server([_TestVideoQueueApi]))

  def tearDown(self):
    self.testbed.deactivate()

  def test_list(self):
    expected_videos = [
      video_queue.Video('video id 0', 'video name 0'),
      video_queue.Video('video id 1', 'video name 1'),
    ]
    self.video_queue_client.list.return_value = expected_videos

    resp = self.app.get(self.API_PREFIX + '/list')
    self.assertEqual(self.get_status_code(resp), 200)
    for video, expected_video in zip(resp.json['videos'], expected_videos):
      self.assertEqual(video['id'], expected_video.id)
      self.assertEqual(video['name'], expected_video.name)

  def test_delete(self):
    resp = self.app.delete(self.API_PREFIX + '/' + self.VIDEO_ID)
    self.video_queue_client.delete.assert_called_with(self.VIDEO_ID)

  # Utility functions

  def get_status_code(self, resp):
    if isinstance(resp.status, basestring):
      return int(resp.status.split(' ')[0])
    else:
      return int(resp.status)

if __name__ == '__main__':
    unittest.main()
