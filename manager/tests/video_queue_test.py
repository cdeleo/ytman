import video_queue

import dpy
import unittest

from google.appengine.ext import testbed

dpy.SetTestMode()

class VideoQueueClientTest(unittest.TestCase):

  USER_ID = 'test@example.com'

  OCTOPUS = video_queue.Video('octopus', 'octopus title')
  PANGOLIN = video_queue.Video('pangolin', 'pangolin title')
  QUETZAL = video_queue.Video('quetzal', 'quetzal title')

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

    self.client = video_queue.VideoQueueClient()
    self.client.push(self.OCTOPUS, user_id=self.USER_ID)
    self.client.push(self.PANGOLIN, user_id=self.USER_ID)

  def assert_queue(self, expected_queue):
    self.assertEqual(self.client.list(user_id=self.USER_ID), expected_queue)
    head = self.client._resolve_pointer(
        self.client._get_pointer_key(self.USER_ID, self.client._HEAD_ID))
    tail = self.client._resolve_pointer(
        self.client._get_pointer_key(self.USER_ID, self.client._TAIL_ID))
    if expected_queue:
      self.assertEqual(head.key.id(), expected_queue[0].id)
      self.assertEqual(tail.key.id(), expected_queue[-1].id)
    else:
      self.assertIsNone(head)
      self.assertIsNone(tail)

  def test_push(self):
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.assert_queue([self.OCTOPUS, self.PANGOLIN, self.QUETZAL])

  def test_pop(self):
    self.assertEqual(self.client.pop(user_id=self.USER_ID), self.OCTOPUS)
    self.assert_queue([self.PANGOLIN])

  def test_pop_empty(self):
    self.client.pop(user_id=self.USER_ID)
    self.client.pop(user_id=self.USER_ID)
    self.client.pop(user_id=self.USER_ID)
    self.assert_queue([])

  def test_insert_front(self):
    self.client.insert_front(self.QUETZAL, user_id=self.USER_ID)
    self.assert_queue([self.QUETZAL, self.OCTOPUS, self.PANGOLIN])

  def test_list(self):
    self.assert_queue([self.OCTOPUS, self.PANGOLIN])

  def test_move_head(self):
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.client.move(self.OCTOPUS.id, 1, user_id=self.USER_ID)
    self.assert_queue([self.PANGOLIN, self.OCTOPUS, self.QUETZAL])

  def test_move_tail(self):
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.client.move(self.QUETZAL.id, 1, user_id=self.USER_ID)
    self.assert_queue([self.OCTOPUS, self.QUETZAL, self.PANGOLIN])

  def test_move_front(self):
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.client.move(self.PANGOLIN.id, 0, user_id=self.USER_ID)
    self.assert_queue([self.PANGOLIN, self.OCTOPUS, self.QUETZAL])

  def test_move_back(self):
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.client.move(self.PANGOLIN.id, 2, user_id=self.USER_ID)
    self.assert_queue([self.OCTOPUS, self.QUETZAL, self.PANGOLIN])

  def test_move_head_front(self):
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.client.move(self.OCTOPUS.id, 0, user_id=self.USER_ID)
    self.assert_queue([self.OCTOPUS, self.PANGOLIN, self.QUETZAL])

  def test_move_tail_back(self):
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.client.move(self.QUETZAL.id, 2, user_id=self.USER_ID)
    self.assert_queue([self.OCTOPUS, self.PANGOLIN, self.QUETZAL])

  def test_push_after_empty(self):
    self.client.pop(user_id=self.USER_ID)
    self.client.pop(user_id=self.USER_ID)
    self.client.push(self.QUETZAL, user_id=self.USER_ID)
    self.assert_queue([self.QUETZAL])

  def test_insert_front_after_empty(self):
    self.client.pop(user_id=self.USER_ID)
    self.client.pop(user_id=self.USER_ID)
    self.client.insert_front(self.QUETZAL, user_id=self.USER_ID)
    self.assert_queue([self.QUETZAL])

if __name__ == '__main__':
    unittest.main()
