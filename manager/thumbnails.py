import base64
import dpy

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
    response = self._thumbnails_service.get(request).execute()
    image_data = response['image_data']
    padding = 4 - (len(image_data) % 4)
    if padding != 4:
      image_data += '=' * padding
    return base64.urlsafe_b64decode(image_data)
