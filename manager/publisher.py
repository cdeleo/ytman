import datetime
import dpy

from google.appengine.ext import ndb

import models

@dpy.Injectable.named('publisher')
class Publisher(object):

  SUCCESS = 0
  TOO_RECENT = 1
  PREVIOUS_FAILURE = 2

  def __init__(self, video_queue_client=dpy.IN):
    self._video_queue_client = video_queue_client

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
          return self.PREVIOUS_FAILURE
        else:
          delta = self._get_now() - status.run_time
          if delta < minimum_run_interval:
            return self.TOO_RECENT

      video = self._video_queue_client.pop()
      models.QueuePublishStatus(
          key=self._get_status_key(user_id),
          run_time=self._get_now(),
          video_id=video.id,
          done=False).put()
      return self.SUCCESS
    return _promote_video()
