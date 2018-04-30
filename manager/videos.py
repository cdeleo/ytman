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

  def __init__(self):
    pass

  @dpy.Inject
  def set_thumbnail(self, video_id, thumbnail_data, youtube_service=dpy.IN):
    youtube_service.thumbnails().set(
        videoId=video_id,
        media_body=MediaIoBaseUpload(
            io.BytesIO(thumbnail_data), mimetype='image/png')).execute()

  @dpy.Inject
  def set_metadata(
      self, video_id, title, subtitle,
      description=None, publish_status=None, youtube_service=dpy.IN):
    parts = ['snippet']
    if publish_status:
      parts.append('status')

    read_response = youtube_service.videos().list(
        id=video_id, part=','.join(parts)).execute()
    video = read_response['items'][0]

    video['snippet']['title'] = '%s - %s' % (title, subtitle)
    if description:
      video['snippet']['description'] = description
    if publish_status:
      video['status']['privacyStatus'] = publish_status

    youtube_service.videos().update(
        part=','.join(parts), body=video).execute()
