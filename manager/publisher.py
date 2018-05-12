import datetime
import dpy

from google.appengine.ext import ndb

import models
import video_queue
import videos

@dpy.Injectable.named('publisher')
class Publisher(object):

  SUCCESS = 0
  TOO_RECENT = 1
  PREVIOUS_FAILURE = 2
  QUEUE_EMPTY = 3

  def __init__(self, video_queue_client=dpy.IN, videos_client=dpy.IN):
    self._video_queue_client = video_queue_client
    self._videos_client = videos_client

  def _get_status_key(self, user_id):
    return ndb.Key(
        models.User, user_id,
        models.QueuePublishStatus, models.QueuePublishStatus.ID)

  def _get_now(self):
    return datetime.datetime.now()

  @dpy.Inject
  def promote_video(self, minimum_run_interval, user_id=dpy.IN):
    @ndb.transactional
    def _promote_video():
      status = self._get_status_key(user_id).get()
      if status:
        if not status.done:
          return self.PREVIOUS_FAILURE, status
        else:
          delta = self._get_now() - status.run_time
          if delta < minimum_run_interval:
            return self.TOO_RECENT, status

      video = self._video_queue_client.pop()
      if not video:
        return self.QUEUE_EMPTY, status
      new_status = models.QueuePublishStatus(
          key=self._get_status_key(user_id),
          run_time=self._get_now(),
          video_id=video.id,
          done=False)
      new_status.put()
      return self.SUCCESS, new_status
    return _promote_video()

  @dpy.Inject
  def finish_video(self, video_id, user_id=dpy.IN):
    @ndb.transactional
    def _finish_video():
      current_status = self._get_status_key(user_id).get()
      if (current_status.done) or (current_status.video_id != video_id):
        return False
      current_status.done = True
      current_status.put()
      return True
    self._videos_client.set_metadata(
        video_id, publish_status=self._videos_client.PUBLIC)
    return _finish_video()
