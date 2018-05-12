import publisher

import datetime
import dpy
import mock
import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

import models
import video_queue
import videos

dpy.SetTestMode()

class PublisherTest(unittest.TestCase):

  USER_ID = 'fake_user_id'
  VIDEO_ID = 'fake_video_id'
  VIDEO_NAME = 'fake_video_name'

  NOW = datetime.datetime(2020, 1, 1)
  MINIMUM_RUN_INTERVAL = datetime.timedelta(hours=1)

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    ndb.get_context().clear_cache()

    self.video_queue_client = mock.Mock()
    self.video_queue_client.pop.return_value = (
        video_queue.Video(self.VIDEO_ID, self.VIDEO_NAME))
    self.videos_client = mock.Mock()
    self.publisher = publisher.Publisher(
        video_queue_client=self.video_queue_client,
        videos_client=self.videos_client)
    self.publisher._get_now = mock.Mock()
    self.publisher._get_now.return_value = self.NOW

  def get_status_key(self):
    return ndb.Key(
        models.User, self.USER_ID,
        models.QueuePublishStatus, models.QueuePublishStatus.ID)

  def set_status(self, run_time, done):
    models.QueuePublishStatus(
        key=self.get_status_key(),
        run_time=run_time,
        video_id=self.VIDEO_ID,
        done=done).put()

  def test_promote_video_first(self):
    result, status = self.publisher.promote_video(
        self.MINIMUM_RUN_INTERVAL, user_id=self.USER_ID)
    self.assertEqual(result, publisher.Publisher.SUCCESS)
    status = self.get_status_key().get()
    self.assertEqual(status.run_time, self.NOW)
    self.assertEqual(status.video_id, self.VIDEO_ID)
    self.assertFalse(status.done)

  def test_promote_video_distant(self):
    previous_run_time = self.NOW - datetime.timedelta(days=1)
    self.set_status(previous_run_time, True)
    result, status = self.publisher.promote_video(
        self.MINIMUM_RUN_INTERVAL, user_id=self.USER_ID)
    self.assertEqual(result, publisher.Publisher.SUCCESS)
    status = self.get_status_key().get()
    self.assertEqual(status.run_time, self.NOW)
    self.assertEqual(status.video_id, self.VIDEO_ID)
    self.assertFalse(status.done)

  def test_promote_video_distant_failure(self):
    previous_run_time = self.NOW - datetime.timedelta(days=1)
    self.set_status(previous_run_time, False)
    result, status = self.publisher.promote_video(
        self.MINIMUM_RUN_INTERVAL, user_id=self.USER_ID)
    self.assertEqual(result, publisher.Publisher.PREVIOUS_FAILURE)
    status = self.get_status_key().get()
    self.assertEqual(status.run_time, previous_run_time)
    self.assertEqual(status.video_id, self.VIDEO_ID)
    self.assertFalse(status.done)

  def test_promote_video_recent(self):
    previous_run_time = self.NOW - datetime.timedelta(minutes=1)
    self.set_status(previous_run_time, True)
    result, status = self.publisher.promote_video(
        self.MINIMUM_RUN_INTERVAL, user_id=self.USER_ID)
    self.assertEqual(result, publisher.Publisher.TOO_RECENT)
    status = self.get_status_key().get()
    self.assertEqual(status.run_time, previous_run_time)
    self.assertEqual(status.video_id, self.VIDEO_ID)
    self.assertTrue(status.done)

  def test_promote_video_recent_failure(self):
    previous_run_time = self.NOW - datetime.timedelta(minutes=1)
    self.set_status(previous_run_time, False)
    result, status = self.publisher.promote_video(
        self.MINIMUM_RUN_INTERVAL, user_id=self.USER_ID)
    self.assertEqual(result, publisher.Publisher.PREVIOUS_FAILURE)
    status = self.get_status_key().get()
    self.assertEqual(status.run_time, previous_run_time)
    self.assertEqual(status.video_id, self.VIDEO_ID)
    self.assertFalse(status.done)

  def test_promote_video_queue_empty(self):
    previous_run_time = self.NOW - datetime.timedelta(days=1)
    self.set_status(previous_run_time, True)
    self.video_queue_client.pop.return_value = None
    result, status = self.publisher.promote_video(
        self.MINIMUM_RUN_INTERVAL, user_id=self.USER_ID)
    self.assertEqual(result, publisher.Publisher.QUEUE_EMPTY)

  def test_finish_video(self):
    self.set_status(self.NOW, False)
    self.assertTrue(
        self.publisher.finish_video(self.VIDEO_ID, user_id=self.USER_ID))
    status = self.get_status_key().get()
    self.assertEqual(status.video_id, self.VIDEO_ID)
    self.assertTrue(status.done)
    self.videos_client.set_metadata.ssert_called_with(
        self.VIDEO_ID, publish_status=videos.VideosClient.PUBLIC)

  def test_finish_video_already_done(self):
    self.set_status(self.NOW, True)
    self.assertFalse(
        self.publisher.finish_video(
            self.VIDEO_ID + '_old', user_id=self.USER_ID))
    self.videos_client.set_metadata.ssert_called_with(
        self.VIDEO_ID, publish_status=videos.VideosClient.PUBLIC)

  def test_finish_video_wrong_video(self):
    self.set_status(self.NOW, True)
    self.assertFalse(
        self.publisher.finish_video(
            self.VIDEO_ID + '_old', user_id=self.USER_ID))
    self.videos_client.set_metadata.ssert_called_with(
        self.VIDEO_ID, publish_status=videos.VideosClient.PUBLIC)

if __name__ == '__main__':
    unittest.main()
