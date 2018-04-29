import images

import collections
import dpy
import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

import models

dpy.SetTestMode()

class _FakeImageWriter(object):

  PREFIX = 'fake_url/'

  def __init__(self):
    self.images = {}

  def write(self, key, data):
    self.images[key] = data
    return self.PREFIX + key

class ImagesTest(unittest.TestCase):

  class TestImage(object):

    def __init__(self, name, data, metadata):
      self.name = name
      self.data = data
      self.metadata = metadata

  USER_ID = 'test@example.com'
  OTHER_USER_ID = 'other@example.com'

  def get_test_image(self, index):
    return self.TestImage(
        'test image %d' % index,
        'test_data_%d' % index,
        {'test_arg': 'test_value_%d' % index})

  def assert_image(self, key, actual, expected):
    self.assertEqual(actual.name, expected.name)
    self.assertEqual(actual.url, _FakeImageWriter.PREFIX + key.urlsafe())
    self.assertEqual(actual.metadata, expected.metadata)

  def assert_images(
      self, user_id, expected_keys_and_images,
      token=None, next_token_should_be_none=True):
    results, token = self.client.list(user_id, token)
    self.assertEqual(len(results), len(expected_keys_and_images))
    for result, (key, expected) in zip(results, expected_keys_and_images):
      self.assert_image(key, result, expected)
    if next_token_should_be_none:
      self.assertIsNone(token)
    else:
      self.assertIsNotNone(token)
    return token

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_search_stub()
    ndb.get_context().clear_cache()

    self.writer = _FakeImageWriter()
    self.client = images.ImagesClient(image_writer=self.writer)
    self.client.set_default_page_size(2)

  def tearDown(self):
    self.testbed.deactivate()

  def test_list(self):
    image = self.get_test_image(0)
    key = self.client.create(
        self.USER_ID, image.name, image.data, image.metadata).key
    self.assert_images(self.USER_ID, [(key, image)])

  def test_list_continue(self):
    keys = []
    for i in xrange(3):
      image = self.get_test_image(i)
      keys.append(
          self.client.create(
              self.USER_ID, image.name, image.data, image.metadata).key)
    token = self.assert_images(
        self.USER_ID,
        [(keys[0], self.get_test_image(0)), (keys[1], self.get_test_image(1))],
        next_token_should_be_none=False)
    self.assert_images(
        self.USER_ID, [(keys[2], self.get_test_image(2))], token=token)

  def test_list_page_size(self):
    for i in xrange(3):
      image = self.get_test_image(i)
      self.client.create(
          self.USER_ID, image.name, image.data, image.metadata)
    self.assertEqual(len(self.client.list(self.USER_ID)[0]), 2);
    self.assertEqual(len(self.client.list(self.USER_ID, page_size=3)[0]), 3);

  def test_list_cross_user(self):
    image = self.get_test_image(0)
    key = self.client.create(
        self.USER_ID, image.name, image.data, image.metadata).key
    self.assert_images(self.OTHER_USER_ID, [])

  def test_get_prefixes(self):
    prefixes = models._get_prefixes('tee test')
    self.assertEqual(set(prefixes), {'t', 'te', 'tee', 'tes', 'test'})

  def run_test_search(self, query, page_size=None):
    keys = []
    for i in xrange(3):
      image = self.get_test_image(i)
      keys.append(
          self.client.create(
              self.USER_ID, image.name, image.data, image.metadata).key)

    if page_size:
      kwargs = {'page_size': page_size}
    else:
      kwargs = {}
    return keys, self.client.search(self.USER_ID, query, **kwargs)

  def test_search_no_results(self):
    _, results = self.run_test_search('absent')
    self.assertEqual(len(results), 0)

  def test_search_empty_query(self):
    _, results = self.run_test_search('')
    self.assertEqual(len(results), 0)

  def test_search_one_result(self):
    keys, results = self.run_test_search('1')
    self.assertEqual(len(results), 1)
    self.assert_image(keys[1], results[0], self.get_test_image(1))

  def test_search_multiple_results(self):
    self.assertEqual(len(self.run_test_search('ima')[1]), 2)
    self.assertEqual(len(self.run_test_search('ima', page_size=3)[1]), 3)

  def test_create(self):
    image = self.get_test_image(0)
    key = self.client.create(
        self.USER_ID, image.name, image.data, image.metadata).key

    result = key.get()
    self.assert_image(key, result, image)
    self.assertEqual(self.writer.images[key.urlsafe()], image.data)
    self.assert_images(self.USER_ID, [(key, image)])

  def prepare_update(self):
    # Initial value
    image = self.get_test_image(0)
    image.metadata['arg_to_update'] = 'value_to_update'
    image.metadata['arg_to_delete'] = 'value_to_delete'
    key = self.client.create(
        self.USER_ID, image.name, image.data, image.metadata).key

    # Delta
    delta = self.get_test_image(0)
    delta.name += ' updated'
    delta.metadata['arg_to_add'] = 'value_added'
    delta.metadata['arg_to_update'] = 'value_updated'
    delta.metadata['arg_to_delete'] = None

    return key, image, delta

  def test_update_with_name(self):
    expected = self.get_test_image(0)
    expected.name += ' updated'
    expected.metadata.update(
        {'arg_to_add': 'value_added', 'arg_to_update': 'value_updated'})

    key, _, delta = self.prepare_update()
    result = self.client.update(self.USER_ID, key, delta, ['name', 'metadata'])
    self.assert_image(key, result, expected)
    self.assert_images(self.USER_ID, [(key, expected)])

  def test_update_without_name(self):
    expected = self.get_test_image(0)
    expected.metadata.update(
        {'arg_to_add': 'value_added', 'arg_to_update': 'value_updated'})

    key, _, delta = self.prepare_update()
    result = self.client.update(self.USER_ID, key, delta, ['metadata'])
    self.assert_image(key, result, expected)
    self.assert_images(self.USER_ID, [(key, expected)])

  def test_update_cross_user(self):
    expected = self.get_test_image(0)
    expected.name += ' updated'
    expected.metadata.update(
        {'arg_to_add': 'value_added', 'arg_to_update': 'value_updated'})

    key, image, delta = self.prepare_update()
    with self.assertRaises(images.CrossUserError):
      self.client.update(self.OTHER_USER_ID, key, delta, ['name', 'metadata'])
    self.assert_images(self.USER_ID, [(key, image)])

  def test_delete(self):
    image = self.get_test_image(0)
    key = self.client.create(
        self.USER_ID, image.name, image.data, image.metadata).key
    self.client.delete(self.USER_ID, key)
    self.assert_images(self.USER_ID, [])

  def test_delete_cross_user(self):
    image = self.get_test_image(0)
    key = self.client.create(
        self.USER_ID, image.name, image.data, image.metadata).key
    with self.assertRaises(images.CrossUserError):
      self.client.delete(self.OTHER_USER_ID, key)
    self.assert_images(self.USER_ID, [(key, image)])

if __name__ == '__main__':
    unittest.main()
