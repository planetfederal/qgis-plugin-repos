import os
import sys
import unittest
from cStringIO import StringIO
from plugins_admin.plugin import Plugin
from plugins_admin.plugin_exceptions import *
from plugins_admin.validator import validator

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

class PluginTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_make_key(self):
        self.assertEqual(Plugin.make_key('uno', 'due'), 'Plugin:uno:due')

    def test_create_from_zip(self):
        """
        Create a Plugin from a zip file
        """
        # Make plugin
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_1.zip')
        zip_file = open(plugin_path, 'rb')
        plugin = Plugin.create_from_zip(zip_file)
        # Check that the plugin is in the database
        key = plugin.get_key()
        self.assertIsNotNone(Plugin(key))

        # Check that the plugin is the same binary blob
        my_zip = open(plugin_path, 'rb')
        plugin_content = my_zip.read()
        self.assertEqual(plugin.blob, plugin_content)
        # Check that metadata are in the DB
        plugin = Plugin(key)
        self.assertEqual(plugin.metadata['name'], 'Test Plugin 1')
        self.assertEqual(plugin.metadata['qgisMinimumVersion'], '2.0')
        self.assertEqual(plugin.metadata['description'], 'This is my first awesome plugin for testing.')
        self.assertEqual(plugin.metadata['version'], '0.1')
        self.assertEqual(plugin.metadata['author'], 'Larry Shaffer (Boundless)')
        self.assertEqual(plugin.metadata['about'], 'Here is some interesting text about my first test plugin.')
        self.assertEqual(plugin.metadata['tracker'], 'https://github.com/boundlessgeo/QGIS/issues')
        self.assertEqual(plugin.metadata['repository'], 'https://github.com/boundlessgeo/QGIS')
        # Recommended items:
        self.assertEqual(plugin.metadata['tags'], 'boundless,test')
        self.assertEqual(plugin.metadata['homepage'], 'http://boundlessgeo.com')
        self.assertEqual(plugin.metadata['category'], 'Plugins')
        self.assertEqual(plugin.metadata['icon'], 'images/test_plugin_1.png')
        self.assertEqual(plugin.metadata['experimental'], 'False')
        self.assertEqual(plugin.metadata['deprecated'], 'False')

        # Delete
        plugin.delete(key)

        # Test
        def load_deleted():
            Plugin(key)
        self.assertRaises(DoesNotExist, load_deleted)

    def test_set_metadata(self):
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_1.zip')
        zip_file = open(plugin_path, 'rb')
        plugin = Plugin.create_from_zip(zip_file)
        # Check that the plugin is in the database
        key = plugin.get_key()
        self.assertIsNotNone(Plugin(key))
        self.assertEqual(plugin.metadata['homepage'], 'http://boundlessgeo.com')
        plugin.set_metadata('homepage', 'http://my.new.homepage')
        plugin = Plugin(key)
        self.assertEqual(plugin.metadata['homepage'], 'http://my.new.homepage')
        # Check blob metadata
        metadata = dict(validator(StringIO(plugin.blob)))
        self.assertEqual(plugin.metadata['homepage'], metadata['homepage'])
        plugin.delete(key)


    def test_set_version(self):
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_1.zip')
        zip_file = open(plugin_path, 'rb')
        plugin = Plugin.create_from_zip(zip_file)
        # Check that the plugin is in the database
        key = plugin.get_key()
        self.assertIsNotNone(Plugin(key))
        plugin.set_metadata('version', '123.34')
        def load_deleted():
            Plugin(key)
        self.assertRaises(DoesNotExist, load_deleted)
        plugin = Plugin(plugin.get_key())
        self.assertEqual(plugin.version, '123.34')
        metadata = dict(validator(StringIO(plugin.blob)))
        self.assertEqual(plugin.metadata['version'], metadata['version'])
        self.assertEqual(plugin.metadata['version'], '123.34')
        plugin.delete(plugin.get_key())

    def test_getter_metadata(self):
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_1.zip')
        zip_file = open(plugin_path, 'rb')
        plugin = Plugin.create_from_zip(zip_file)
        # Check that the plugin is in the database
        key = plugin.get_key()
        self.assertIsNotNone(Plugin(key))
        self.assertEqual(plugin.metadata['homepage'], 'http://boundlessgeo.com')
        self.assertEqual(plugin.metadata['homepage'], plugin.homepage)
        plugin.delete(key)

    def test_getter_metadata_empty(self):
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_1.zip')
        zip_file = open(plugin_path, 'rb')
        plugin = Plugin.create_from_zip(zip_file)
        # Check that the plugin is in the database
        key = plugin.get_key()
        self.assertIsNotNone(Plugin(key))
        self.assertEquals(plugin.not_exists, '')
        plugin.delete(key)

if __name__ == '__main__':
    unittest.main()
