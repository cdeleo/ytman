import endpoints

import constants
import images_api
import users_api
import video_queue_api
import videos_api

api_collection = endpoints.api(
    name='ytman', version='v1', allowed_client_ids=constants.CLIENT_IDS)

ImagesApi = api_collection.api_class(resource_name='images', path='images')(
    images_api.ImagesApi)
UsersApi = api_collection.api_class(resource_name='users', path='users')(
    users_api.UsersApi)
VideosApi = api_collection.api_class(resource_name='videos', path='videos')(
    videos_api.VideosApi)
VideoQueueApi = api_collection.api_class(
    resource_name='video_queue', path='video_queue')(
        video_queue_api.VideoQueueApi)

api = endpoints.api_server([api_collection])
