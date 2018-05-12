import cron

import dpy
import mock
import unittest

from google.appengine.ext import testbed

import models
import publisher
import video_queue

dpy.SetTestMode()

class CronPublishTest(unittest.TestCase):

  USER_ID = 'fake_user_id'
  VIDEO_ID = 'fake_video_id'

  TEST_VIDEO = video_queue.Video(id=VIDEO_ID, name='fake_video_name')
  TEST_STATUS = models.QueuePublishStatus(video_id=VIDEO_ID)

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

    self.video_queue_client = video_queue.VideoQueueClient()

    self.publisher = mock.Mock()
    self.publish_handler = cron.PublishHandler()

  def test_users_with_queues(self):
    self.video_queue_client.push(self.TEST_VIDEO, user_id=self.USER_ID)
    self.assertEqual(
        self.publish_handler._users_with_queues(), {self.USER_ID})

  def test_users_with_queues_empty(self):
    self.assertEqual(self.publish_handler._users_with_queues(), set())

  def test_users_with_queues_empty_pointer(self):
    self.video_queue_client.push(self.TEST_VIDEO, user_id=self.USER_ID)
    self.video_queue_client.pop(user_id=self.USER_ID)
    self.assertEqual(self.publish_handler._users_with_queues(), set())

  def test_handle_user_promote_success(self):
    self.publisher.promote_video.return_value = (
        publisher.Publisher.SUCCESS, self.TEST_STATUS)
    self.publish_handler._handle_user(
        user_id=self.USER_ID, publisher=self.publisher)
    self.publisher.finish_video.assert_called_with(self.VIDEO_ID)

  def test_handle_user_promote_too_recent(self):
    self.publisher.promote_video.return_value = (
        publisher.Publisher.TOO_RECENT, self.TEST_STATUS)
    self.publish_handler._handle_user(
        user_id=self.USER_ID, publisher=self.publisher)
    self.publisher.finish_video.assert_not_called()

  def test_handle_user_promote_previous_failure(self):
    self.publisher.promote_video.return_value = (
        publisher.Publisher.PREVIOUS_FAILURE, self.TEST_STATUS)
    self.publish_handler._handle_user(
        user_id=self.USER_ID, publisher=self.publisher)
    self.publisher.finish_video.assert_called_with(self.VIDEO_ID)

  def test_handle_user_promote_queue_empty(self):
    self.publisher.promote_video.return_value = (
        publisher.Publisher.TOO_RECENT, self.TEST_STATUS)
    self.publish_handler._handle_user(
        user_id=self.USER_ID, publisher=self.publisher)
    self.publisher.finish_video.assert_not_called()

if __name__ == '__main__':
    unittest.main()
