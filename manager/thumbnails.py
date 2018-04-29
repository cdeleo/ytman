import base64
import dpy
import httplib2

from apiclient import discovery

import auth

@dpy.Injectable.named('thumbnails_service')
@dpy.Singleton
def _provide_thumbnails_service(credentials=dpy.IN):
  http = httplib2.Http()
  http = credentials.authorize(http)

  api_root = 'https://thumbnails-dot-youtube-manager-196811.appspot.com/_ah/api'
  api = 'thumbnails'
  version = 'v1'
  discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
  return discovery.build(
      api, version, discoveryServiceUrl=discovery_url, http=http)

@dpy.Injectable.named('thumbnails_client')
class ThumbnailsClient(object):

  def __init__(self, thumbnails_service=dpy.IN):
    self._thumbnails_service = thumbnails_service

  def get(self, bg_key, title, subtitle):
    request = {
      'bg_key': bg_key,
      'title': title,
      'subtitle': subtitle,
    }
    response = self._thumbnails_service.get(**request).execute()
    image_data = str(response['image_data'])
    padding = 4 - (len(image_data) % 4)
    if padding != 4:
      image_data += '=' * padding
    return base64.urlsafe_b64decode(image_data)
