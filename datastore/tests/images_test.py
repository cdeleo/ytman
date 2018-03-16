import images

import collections
import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed

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

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    ndb.get_context().clear_cache()

    self.writer = _FakeImageWriter()
    self.client = images.ImageClient(writer=self.writer, page_size=2)

  def tearDown(self):
    self.testbed.deactivate()

  def test_list(self):
    image = self.get_test_image(0)
    key = self.client.create(image.name, image.data, image.metadata)

    results, token = self.client.list()
    self.assertEqual(len(results), 1)
    self.assert_image(key, results[0], image)
    self.assertIsNone(token)

  def test_list_continue(self):
    keys = []
    for i in xrange(3):
      image = self.get_test_image(i)
      keys.append(self.client.create(image.name, image.data, image.metadata))

    results, token = self.client.list()
    self.assertEqual(len(results), 2)
    self.assert_image(keys[0], results[0], self.get_test_image(0))
    self.assert_image(keys[1], results[1], self.get_test_image(1))
    self.assertIsNotNone(token)

    results, token = self.client.list(token)
    self.assertEqual(len(results), 1)
    self.assert_image(keys[2], results[0], self.get_test_image(2))
    self.assertIsNone(token)

  def run_test_search(self, query):
    keys = []
    for i in xrange(3):
      image = self.get_test_image(i)
      keys.append(self.client.create(image.name, image.data, image.metadata))

    return keys, self.client.search(query)

  def test_search_no_results(self):
    keys, results = self.run_test_search('absent')
    self.assertEqual(len(results), 0)

  def test_search_one_result(self):
    keys, results = self.run_test_search('1')
    self.assertEqual(len(results), 1)
    self.assert_image(keys[1], results[0], self.get_test_image(1))

  def test_search_multiple_results(self):
    keys, results = self.run_test_search('ima')
    self.assertEqual(len(results), 3)
    for i, (key, result) in enumerate(zip(keys, results)):
      self.assert_image(key, result, self.get_test_image(i))

  def test_create(self):
    image = self.get_test_image(0)
    key = self.client.create(image.name, image.data, image.metadata)

    result = ndb.Key(urlsafe=key).get()
    self.assert_image(key, result, image)
    self.assertEqual(self.writer.images[key], image.data)

  def run_test_update(self, mask):
    # Initial value
    image = self.get_test_image(0)
    image.metadata['arg_to_update'] = 'value_to_update'
    image.metadata['arg_to_delete'] = 'value_to_delete'
    key = self.client.create(image.name, image.data, image.metadata)

    # Delta
    delta = self.get_test_image(0)
    delta.name += ' updated'
    delta.metadata['arg_to_add'] = 'value_added'
    delta.metadata['arg_to_update'] = 'value_updated'
    delta.metadata['arg_to_delete'] = None
    return key, self.client.update(key, delta, mask)

  def test_update_with_name(self):
    expected = self.get_test_image(0)
    expected.name += ' updated'
    expected.metadata.update(
        {'arg_to_add': 'value_added', 'arg_to_update': 'value_updated'})

    key, result = self.run_test_update(['name', 'metadata'])
    self.assert_image(key, result, expected)

  def test_update_without_name(self):
    expected = self.get_test_image(0)
    expected.metadata.update(
        {'arg_to_add': 'value_added', 'arg_to_update': 'value_updated'})

    key, result = self.run_test_update(['metadata'])
    self.assert_image(key, result, expected)

  def test_delete(self):
    image = self.get_test_image(0)
    key = self.client.create(image.name, image.data, image.metadata)
    self.client.delete(key)

    results, token = self.client.list()
    self.assertEqual(len(results), 0)

  def get_test_image(self, index):
    return self.TestImage(
        'test image %d' % index,
        'test_data_%d' % index,
        {'test_arg': 'test_value_%d' % index})

  def assert_image(self, key, actual, expected):
    self.assertEqual(actual.name, expected.name)
    self.assertEqual(actual.url, _FakeImageWriter.PREFIX + key)
    self.assertEqual(actual.metadata, expected.metadata)

if __name__ == '__main__':
    unittest.main()
