import datetime
import dpy
import webapp2

import models
import publisher

class PublishHandler(webapp2.RequestHandler):

  MINIMUM_RUN_INTERVAL = datetime.timedelta(minutes=45)
  NEEDS_FINISHING_RESULTS = {
      publisher.Publisher.SUCCESS, publisher.Publisher.PREVIOUS_FAILURE}

  def _users_with_queues(self):
    q = models.EnqueuedVideoPointer.query(
        models.EnqueuedVideoPointer.video_key != None)
    return {key.pairs()[0][1] for key in q.iter(keys_only=True)}

  @dpy.Scope
  def _handle_user(self, user_id, publisher):
    dpy.Injectable.value(user_id=user_id)
    r, status = publisher.promote_video(self.MINIMUM_RUN_INTERVAL)

    if r in self.NEEDS_FINISHING_RESULTS:
      publisher.finish_video(status.video_id)

  @dpy.Inject
  def get(self, publisher=dpy.IN):
    for user_id in self._users_with_queues():
      self._handle_user(user_id, publisher)

app = webapp2.WSGIApplication([
    ('/cron/publish', PublishHandler),
])
