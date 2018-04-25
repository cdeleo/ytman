import base64
import endpoints
import json

from protorpc import message_types
from protorpc import messages
from protorpc import remote

import images

# Common messages

class MetadataPair(messages.Message):
  key = messages.StringField(1)
  value = messages.StringField(2)

class Image(messages.Message):
  key = messages.StringField(1)
  name = messages.StringField(2)
  url = messages.StringField(3)
  metadata = messages.MessageField(MetadataPair, 4, repeated=True)

# List

LIST_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    token=messages.StringField(1),
    page_size=messages.IntegerField(2))

class ListResponse(messages.Message):
  images = messages.MessageField(Image, 1, repeated=True)
  token = messages.StringField(2)

# Search

SEARCH_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    q=messages.StringField(1),
    page_size=messages.IntegerField(2))

class SearchResponse(messages.Message):
  images = messages.MessageField(Image, 1, repeated=True)

# Create

class CreateRequest(messages.Message):
  name = messages.StringField(1)
  data = messages.StringField(2)
  metadata = messages.MessageField(MetadataPair, 3, repeated=True)

class CreateResponse(messages.Message):
  image = messages.MessageField(Image, 1)

# Update

class UpdateRequest(messages.Message):
  delta = messages.MessageField(Image, 1)
  mask = messages.StringField(2, repeated=True)

UPDATE_RESOURCE = endpoints.ResourceContainer(
    UpdateRequest,
    key=messages.StringField(3))

class UpdateResponse(messages.Message):
  image = messages.MessageField(Image, 1)

# Delete

DELETE_RESOURCE = endpoints.ResourceContainer(
    message_types.VoidMessage,
    key=messages.StringField(1))

class DeleteResponse(messages.Message):
  pass

# Service

class ImagesApi(remote.Service):

  MAX_PAGE_SIZE = 25

  def __init__(self):
    self.client = images.ImagesClient()

  @classmethod
  def get_page_size(cls, page_size):
    return min((page_size, cls.MAX_PAGE_SIZE)) if page_size else None

  @classmethod
  def image_model_to_proto(cls, model):
    proto = Image()
    proto.key = model.key.urlsafe()
    proto.name = model.name
    proto.url = model.url
    proto.metadata = cls.metadata_model_to_proto(model.metadata)
    return proto

  @classmethod
  def metadata_model_to_proto(cls, model_metadata):
    return [MetadataPair(key=k, value=v) for k, v in model_metadata.iteritems()]

  @classmethod
  def delta_proto_to_model(cls, proto_delta):
    model = images.Image()
    model.name = proto_delta.name
    model.metadata = cls.metadata_proto_to_model(proto_delta.metadata)
    return model

  @classmethod
  def metadata_proto_to_model(cls, proto_metadata):
    return {p.key: p.value for p in proto_metadata}

  @classmethod
  def get_current_user_id(cls):
    user = endpoints.get_current_user()
    if not user:
      raise endpoints.UnauthorizedException
    return user.user_id()

  @endpoints.method(
      LIST_RESOURCE,
      ListResponse,
      path='list',
      http_method='GET',
      name='list')
  def list_handler(self, req):
    kwargs = {}
    if req.token:
      kwargs['token'] = req.token
    if req.page_size:
      kwargs['page_size'] = self.get_page_size(req.page_size)
    images, next_token = self.client.list(self.get_current_user_id(), **kwargs)
    resp = ListResponse()
    resp.images = [self.image_model_to_proto(r) for r in images]
    if next_token:
      resp.token = next_token
    return resp

  @endpoints.method(
      SEARCH_RESOURCE,
      SearchResponse,
      path='search',
      http_method='GET',
      name='search')
  def search_handler(self, req):
    kwargs = {}
    if req.page_size:
      kwargs['page_size'] = self.get_page_size(req.page_size)
    images = self.client.search(self.get_current_user_id(), req.q, **kwargs)
    resp = SearchResponse()
    resp.images = [self.image_model_to_proto(r) for r in images]
    return resp

  DATA_PREFIX = 'data:image/png;base64,'

  @classmethod
  def _decode_data(cls, data):
    if not data.startswith(cls.DATA_PREFIX):
      raise ValueError('Incorrect image format')
    return base64.urlsafe_b64decode(str(data[len(cls.DATA_PREFIX):]))

  @endpoints.method(
      CreateRequest,
      CreateResponse,
      path='create',
      http_method='POST',
      name='create')
  def create_handler(self, req):
    image = self.client.create(
        self.get_current_user_id(),
        req.name,
        self._decode_data(req.data),
        self.metadata_proto_to_model(req.metadata))
    resp = CreateResponse()
    resp.image = self.image_model_to_proto(image)
    return resp

  @endpoints.method(
      UPDATE_RESOURCE,
      UpdateResponse,
      path='{key}',
      http_method='PUT',
      name='update')
  def update_handler(self, req):
    image = self.client.update(
        self.get_current_user_id(),
        self.client.parse_key(req.key),
        self.delta_proto_to_model(req.delta),
        req.mask)
    resp = UpdateResponse()
    resp.image = self.image_model_to_proto(image)
    return resp

  @endpoints.method(
      DELETE_RESOURCE,
      DeleteResponse,
      path='{key}',
      http_method='DELETE',
      name='delete')
  def delete_handler(self, req):
    self.client.delete(
        self.get_current_user_id(), self.client.parse_key(req.key))
    return DeleteResponse()
