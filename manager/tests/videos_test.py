import videos

import copy
import dpy
import mock
import unittest

dpy.SetTestMode()

class VideosClientTest(unittest.TestCase):

  VIDEO_ID = 'fake_video_id'
  TITLE = 'fake_title'
  SUBTITLE = 'fake_subtitle'
  NAME = videos.VideosClient.get_video_name(TITLE, SUBTITLE)
  DESCRIPTION = 'fake_description'
  THUMBNAIL_DATA = 'fake_thumbnail_data'

  VIDEO_RESOURCE = {
    'snippet': {},
    'status': {},
  }

  def setUp(self):
    self.youtube_service = mock.Mock()
    self.youtube_service.videos().list().execute.return_value = {
        'items': [self.VIDEO_RESOURCE],
    }
    self.client = videos.VideosClient()

  def test_set_thumbnail(self):
    self.client.set_thumbnail(
        self.VIDEO_ID, self.THUMBNAIL_DATA,
        youtube_service=self.youtube_service)

    self.youtube_service.thumbnails().set.assert_called_with(
        videoId=self.VIDEO_ID, media_body=mock.ANY)
    body = self.youtube_service.thumbnails().set.call_args[1]['media_body']
    body.stream().seek(0)
    self.assertEqual(body.stream().read(), self.THUMBNAIL_DATA)
    self.assertEqual(body.mimetype(), 'image/png')
    self.youtube_service.thumbnails().set().execute.assert_called_with()

  def _check_set_metadata(self, expected_part, expected_body):
    self.youtube_service.videos().list.assert_called_with(
        id=self.VIDEO_ID, part=expected_part)
    self.youtube_service.videos().list().execute.assert_called_with()

    self.youtube_service.videos().update.assert_called_with(
        part=expected_part, body=expected_body)
    self.youtube_service.videos().update().execute.assert_called_with()

  def test_set_metadata(self):
    self.client.set_metadata(
        self.VIDEO_ID, title=self.NAME, youtube_service=self.youtube_service)
    expected_body = copy.deepcopy(self.VIDEO_RESOURCE)
    expected_body['snippet']['title'] = self.NAME
    self._check_set_metadata('snippet', expected_body)

  def test_set_metadata_description(self):
    self.client.set_metadata(
        self.VIDEO_ID,
        title=self.NAME,
        description=self.DESCRIPTION,
        youtube_service=self.youtube_service)
    expected_body = copy.deepcopy(self.VIDEO_RESOURCE)
    expected_body['snippet']['title'] = self.NAME
    expected_body['snippet']['description'] = self.DESCRIPTION
    self._check_set_metadata('snippet', expected_body)

  def test_set_metadata_publish_status(self):
    self.client.set_metadata(
        self.VIDEO_ID,
        title=self.NAME,
        publish_status=self.client.PRIVATE,
        youtube_service=self.youtube_service)
    expected_body = copy.deepcopy(self.VIDEO_RESOURCE)
    expected_body['snippet']['title'] = self.NAME
    expected_body['status']['privacyStatus'] = self.client.PRIVATE
    self._check_set_metadata('snippet,status', expected_body)

  def test_set_metadata_none(self):
    self.client.set_metadata(
        self.VIDEO_ID, youtube_service=self.youtube_service)
    self.youtube_service.videos().list().execute.assert_not_called()
    self.youtube_service.videos().update().execute.assert_not_called()

if __name__ == '__main__':
  unittest.main()
