import dpy
import httplib2
import io

from apiclient import discovery
from apiclient.http import MediaIoBaseUpload

import auth

@dpy.Injectable.named('youtube_service')
@dpy.Singleton
def _provide_youtube_service(credentials=dpy.IN):
  http = httplib2.Http()
  http = credentials.authorize(http)

  api_root = 'https://www.googleapis.com'
  api = 'youtube'
  version = 'v3'
  discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
  return discovery.build(
      api, version, discoveryServiceUrl=discovery_url, http=http)

@dpy.Injectable.named('videos_client')
class VideosClient(object):

  def __init__(self, youtube_service=dpy.IN):
    self._youtube_service = youtube_service

  def set_thumbnail(self, video_id, thumbnail_data):
    request = {
      'videoId': video_id,
      'media_body': MediaIoBaseUpload(
          io.BytesIO(thumbnail_data), mimetype='image/png'),
    }
    self._youtube_service.thumbnails().set(**request).execute()

  def set_metadata(self, video_id, description=None, publish_status=None):
    pass
