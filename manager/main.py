import endpoints
import images_api
import videos_api

CONSOLE_CLIENT_ID = '955262123852-j4nv7slhidt5lcjve721nj9lo8otmfq5.apps.googleusercontent.com'
WEB_CLIENT_ID = '955262123852-c1gthms5mhs36q6njvg6kgqu4f1b09q7.apps.googleusercontent.com'
CLIENT_IDS = [CONSOLE_CLIENT_ID, WEB_CLIENT_ID]

api_collection = endpoints.api(name='ytman', version='v1', allowed_client_ids=CLIENT_IDS)

ImagesApi = api_collection.api_class(resource_name='images', path='images')(
    images_api.ImagesApi)
VideosApi = api_collection.api_class(resource_name='videos', path='videos')(
    videos_api.VideosApi)

api = endpoints.api_server([api_collection])
