import videos_api

import dpy
import endpoints
import mock
import unittest
import webtest

from google.appengine.ext import testbed

import thumbnails
import video_queue
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
    self.videos_client.PRIVATE = videos.VideosClient.PRIVATE
    self.videos_client.PUBLIC = videos.VideosClient.PUBLIC
    self.videos_client.get_video_name.return_value = (
        videos.VideosClient.get_video_name(self.TITLE, self.SUBTITLE))

    self.video_queue_client = mock.Mock(video_queue.VideoQueueClient)

    @endpoints.api(name='videos', version='v1')
    class _TestVideosApi(videos_api.VideosApi):

      def __init__(inner_self):
        super(_TestVideosApi, inner_self).__init__(
            thumbnails_client=self.thumbnails_client,
            videos_client=self.videos_client,
            video_queue_client=self.video_queue_client)

    self.app = webtest.TestApp(endpoints.api_server([_TestVideosApi]))

  def tearDown(self):
    self.testbed.deactivate()

  def check_publish(self, publish_mode, expected_publish_status):
    req = {
      'video_id': self.VIDEO_ID,
      'bg_key': self.BG_KEY,
      'title': self.TITLE,
      'subtitle': self.SUBTITLE,
      'description': self.DESCRIPTION,
    }
    if publish_mode:
      req['publish_mode'] = publish_mode.number
    resp = self.app.post_json(self.API_PREFIX + '/publish', req)
    self.assertEqual(self.get_status_code(resp), 200)
    self.thumbnails_client.get.assert_called_with(
        self.BG_KEY, self.TITLE, self.SUBTITLE)
    self.videos_client.set_thumbnail.assert_called_with(
        self.VIDEO_ID, self.THUMBNAIL_DATA)
    expected_name = videos.VideosClient.get_video_name(
        self.TITLE, self.SUBTITLE)
    self.videos_client.set_metadata.assert_called_with(
        self.VIDEO_ID,
        title=expected_name,
        description=self.DESCRIPTION,
        publish_status=expected_publish_status)

  def test_publish_none(self):
    self.check_publish(None, videos.VideosClient.PRIVATE)
    self.video_queue_client.push.assert_not_called()
    self.video_queue_client.insert_front.assert_not_called()

  def test_publish_now(self):
    self.check_publish(
        videos_api.PublishRequest.PublishMode.NOW, videos.VideosClient.PUBLIC)
    self.video_queue_client.push.assert_not_called()
    self.video_queue_client.insert_front.assert_not_called()

  def test_publish_enqueue(self):
    self.check_publish(
        videos_api.PublishRequest.PublishMode.ENQUEUE,
        videos.VideosClient.PRIVATE)
    self.video_queue_client.push.assert_called_with(
        video_queue.Video(
            id=self.VIDEO_ID,
            name=videos.VideosClient.get_video_name(self.TITLE, self.SUBTITLE)))
    self.video_queue_client.insert_front.assert_not_called()

  def test_publish_preempt(self):
    self.check_publish(
        videos_api.PublishRequest.PublishMode.PREEMPT,
        videos.VideosClient.PRIVATE)
    self.video_queue_client.push.assert_not_called()
    self.video_queue_client.insert_front.assert_called_with(
        video_queue.Video(
            id=self.VIDEO_ID,
            name=videos.VideosClient.get_video_name(self.TITLE, self.SUBTITLE)))

  def test_list_queue(self):
    expected_videos = [
      video_queue.Video('video id 0', 'video name 0'),
      video_queue.Video('video id 1', 'video name 1'),
    ]
    self.video_queue_client.list.return_value = expected_videos

    resp = self.app.get(self.API_PREFIX + '/list_queue')
    self.assertEqual(self.get_status_code(resp), 200)
    for video, expected_video in zip(resp.json['videos'], expected_videos):
      self.assertEqual(video['id'], expected_video.id)
      self.assertEqual(video['name'], expected_video.name)

  # Utility functions

  def get_status_code(self, resp):
    if isinstance(resp.status, basestring):
      return int(resp.status.split(' ')[0])
    else:
      return int(resp.status)

if __name__ == '__main__':
    unittest.main()
