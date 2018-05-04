import collections
import dpy

from google.appengine.ext import ndb

import models

Video = collections.namedtuple('Video', ['id', 'name'])

@dpy.Injectable.named('video_queue_client')
class VideoQueueClient(object):

  _HEAD_ID = models.EnqueuedVideoPointer.HEAD_ID
  _TAIL_ID = models.EnqueuedVideoPointer.TAIL_ID

  def __init__(self):
    pass

  def _get_pointer_key(self, user_id, pointer_id):
    return ndb.Key(
        models.User,
        user_id,
        models.EnqueuedVideoPointer,
        pointer_id)

  def _get_pointer_entity(self, pointer_key, video_key):
    return models.EnqueuedVideoPointer(key=pointer_key, video_key=video_key)

  def _resolve_pointer(self, pointer_key):
    pointer = pointer_key.get()
    if pointer is not None and pointer.video_key is not None:
      return pointer.video_key.get()
    else:
      return None

  def _get_video_entity(self, user_id, video):
    return models.EnqueuedVideo(
        key=ndb.Key(models.User, user_id, models.EnqueuedVideo, video.id),
        name=video.name)

  @ndb.transactional
  def _insert(self, user_id, end_id, video, adjust_f):
    end_pointer_key = self._get_pointer_key(user_id, end_id)
    end = self._resolve_pointer(end_pointer_key)

    video_entity = self._get_video_entity(user_id, video)
    end_pointer = self._get_pointer_entity(end_pointer_key, video_entity.key)
    to_put = [video_entity, end_pointer]

    if end is None:
      other_end_id = self._TAIL_ID if end_id == self._HEAD_ID else self._HEAD_ID
      other_end_pointer = self._get_pointer_entity(
          self._get_pointer_key(user_id, other_end_id), video_entity.key)
      to_put.append(other_end_pointer)
    else:
      additional_to_put = adjust_f(video_entity, end)
      if additional_to_put:
        to_put.extend(additional_to_put)
    ndb.put_multi(to_put)

  @dpy.Inject
  def push(self, video, user_id=dpy.IN):
    def _adjust_f(video_entity, tail):
      tail.next_key = video_entity.key
      return [tail]
    self._insert(user_id, self._TAIL_ID, video, _adjust_f)

  @dpy.Inject
  def pop(self, user_id=dpy.IN):
    @ndb.transactional
    def _pop():
      head_pointer_key = self._get_pointer_key(user_id, self._HEAD_ID)
      head = self._resolve_pointer(head_pointer_key)
      if head is None:
        return None

      head_pointer = self._get_pointer_entity(head_pointer_key, head.next_key)
      to_put = [head_pointer]
      if head.next_key is None:
        tail_pointer = self._get_pointer_entity(
            self._get_pointer_key(user_id, self._TAIL_ID), None)
        to_put.append(tail_pointer)
      ndb.put_multi(to_put)
      head.key.delete()
      return Video(id=head.key.id(), name=head.name)
    return _pop()

  @dpy.Inject
  def insert_front(self, video, user_id=dpy.IN):
    def _adjust_f(video_entity, head):
      video_entity.next_key = head.key
    self._insert(user_id, self._HEAD_ID, video, _adjust_f)

  def _get_videos(self, user_id):
    fetched_videos = models.EnqueuedVideo.query(
        ancestor=ndb.Key(models.User, user_id)).fetch()
    videos_map = {v.next_key: v for v in fetched_videos}
    videos = []
    current = videos_map.get(None)
    while current:
      videos.append(current)
      current = videos_map.get(current.key)
    videos.reverse()
    return videos

  @dpy.Inject
  def list(self, user_id=dpy.IN):
    return [Video(id=v.key.id(), name=v.name)
            for v in self._get_videos(user_id)]

  def _insert_at(self, user_id, videos, index, video):
    to_put = [video]
    if index == 0:
      video.next_key = videos[0].key
      head_pointer = self._get_pointer_entity(
          self._get_pointer_key(user_id, self._HEAD_ID), video.key)
      to_put.append(head_pointer)
    else:
      previous = videos[index - 1]
      video.next_key = previous.next_key
      previous.next_key = video.key
      to_put.append(previous)
      if index == len(videos):
        tail_pointer = self._get_pointer_entity(
            self._get_pointer_key(user_id, self._TAIL_ID), video.key)
        to_put.append(tail_pointer)
    return to_put

  def _remove_at(self, user_id, videos, index):
    to_put = []
    if index == 0:
      head_pointer = self._get_pointer_entity(
          self._get_pointer_key(user_id, self._HEAD_ID), videos[index].next_key)
      to_put.append(head_pointer)
    else:
      previous = videos[index - 1]
      previous.next_key = videos[index].next_key
      to_put.append(previous)
      if index == len(videos) - 1:
        tail_pointer = self._get_pointer_entity(
            self._get_pointer_key(user_id, self._TAIL_ID), previous.key)
        to_put.append(tail_pointer)
    del videos[index]
    return to_put

  def _find_video(self, videos, video_id):
    for index in xrange(len(videos)):
      if videos[index].key.id() == video_id:
        return index
    raise Exception('Video %s not enqueued.' % video_id)

  @dpy.Inject
  def move(self, video_id, dst_index, user_id=dpy.IN):
    @ndb.transactional
    def _move():
      videos = self._get_videos(user_id)
      if len(videos) <= dst_index:
        raise Exception('Only %d videos enqueued.' % len(videos))
      src_index = self._find_video(videos, video_id)
      if src_index == dst_index:
        return

      to_put = []
      video = videos[src_index]
      to_put.extend(self._remove_at(user_id, videos, src_index))
      to_put.extend(self._insert_at(user_id, videos, dst_index, video))
      ndb.put_multi(to_put)
    _move()

  @dpy.Inject
  def delete(self, video_id, user_id=dpy.IN):
    @ndb.transactional
    def _delete():
      videos = self._get_videos(user_id)
      index = self._find_video(videos, video_id)
      video = videos[index]
      ndb.put_multi(self._remove_at(user_id, videos, index))
      video.key.delete()
    _delete()
