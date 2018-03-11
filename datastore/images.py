import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

# Common messages

class Image(messages.Message):
  id = messages.StringField(1)
  name = messages.StringField(2)
  data = messages.StringField(3)

# List

LIST_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    token=messages.StringField(1))

class ListResponse(messages.Message):
  images = messages.MessageField(Image, 1, repeated=True)
  token = messages.StringField(2)

# Search

SEARCH_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    q=messages.StringField(1))

class SearchResponse(messages.Message):
  images = messages.MessageField(Image, 1, repeated=True)

# Create

class CreateRequest(messages.Message):
  image = messages.MessageField(Image, 1)

class CreateResponse(messages.Message):
  id = messages.StringField(1)

# Update

class UpdateRequest(messages.Message):
  image = messages.MessageField(Image, 1)
  mask = messages.StringField(2, repeated=True)

UPDATE_RESOURCE = endpoints.ResourceContainer(
    UpdateRequest,
    id=messages.StringField(3))

class UpdateResponse(messages.Message):
  image = messages.MessageField(Image, 1)

# Delete

DELETE_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    id=messages.StringField(1))

class DeleteResponse(messages.Message):
  pass

# Service

@endpoints.api(name='images', version='v1')
class ImagesApi(remote.Service):

  @endpoints.method(
      LIST_RESOURCE,
      ListResponse,
      path='list',
      http_method='GET',
      name='list')
  def list_handler(self, request):
    return ListResponse()

  @endpoints.method(
      LIST_RESOURCE,
      ListResponse,
      path='list/{token}',
      http_method='GET',
      name='list_continue')
  def list_continue_handler(self, request):
    return ListResponse()

  @endpoints.method(
      SEARCH_RESOURCE,
      SearchResponse,
      path='search/{q}',
      http_method='GET',
      name='search')
  def search_handler(self, request):
    return SearchResponse()

  @endpoints.method(
      CreateRequest,
      CreateResponse,
      path='create',
      http_method='POST',
      name='create')
  def create_handler(self, request):
    return CreateResponse(id='fake_id')

  @endpoints.method(
      UPDATE_RESOURCE,
      UpdateResponse,
      path='{id}',
      http_method='PUT',
      name='update')
  def update_handler(self, request):
    return UpdateResponse()

  @endpoints.method(
      DELETE_RESOURCE,
      DeleteResponse,
      path='{id}',
      http_method='DELETE',
      name='delete')
  def delete_handler(self, request):
    return DeleteResponse()
