# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
Test the Plugin class
Author: Alessandro Pasotti

"""
import os
import unittest
from cStringIO import StringIO
from plugins_admin.plugin import Plugin
from plugins_admin.plugin_exceptions import *
from plugins_admin.validator import validator
from .utils import BaseTest, DATA_DIR

class PluginTestCase(BaseTest):


    def test_make_key(self):
        self.assertEqual(Plugin.make_key('uno', 'due'), 'Plugin:uno:due')

    def test_load_from_zip(self):
        """
        Create a Plugin from a zip file
        """
        # Make plugin
        plugin = self.load_from_zip()
        # Check that the plugin is in the database
        key = plugin.key
        self.assertIsNotNone(Plugin(key))

        # Check that the plugin is the same binary blob
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_%s.zip'  % 1)
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
        plugin = self.load_from_zip()
        # Check that the plugin is in the database
        key = plugin.key
        self.assertIsNotNone(Plugin(key))
        self.assertEqual(plugin.metadata['homepage'], 'http://boundlessgeo.com')
        plugin.set_metadata('homepage', 'http://my.new.homepage')
        plugin = Plugin(key)
        self.assertEqual(plugin.metadata['homepage'], 'http://my.new.homepage')
        # Check blob metadata
        metadata = dict(validator(StringIO(plugin.blob)))
        self.assertEqual(plugin.metadata['homepage'], metadata['homepage'])


    def test_set_version(self):
        plugin = self.load_from_zip()
        # Check that the plugin is in the database
        key = plugin.key
        self.assertIsNotNone(Plugin(key))
        plugin.set_metadata('version', '123.34')
        def load_deleted():
            Plugin(key)
        self.assertRaises(DoesNotExist, load_deleted)
        plugin = Plugin(plugin.key)
        self.assertEqual(plugin.version, '123.34')
        metadata = dict(validator(StringIO(plugin.blob)))
        self.assertEqual(plugin.metadata['version'], metadata['version'])
        self.assertEqual(plugin.metadata['version'], '123.34')

    def test_getter_metadata(self):
        plugin = self.load_from_zip()
        # Check that the plugin is in the database
        key = plugin.key
        self.assertIsNotNone(Plugin(key))
        self.assertEqual(plugin.metadata['homepage'], 'http://boundlessgeo.com')
        self.assertEqual(plugin.metadata['homepage'], plugin.homepage)

    def test_getter_metadata_empty(self):
        plugin = self.load_from_zip()
        # Check that the plugin is in the database
        key = plugin.key
        self.assertIsNotNone(Plugin(key))
        self.assertEquals(plugin.not_exists, '')

    def test_plugin_version(self):
        """Test that only the compatible plugins are returned by all(version)

        Test versions:
        test_plugin_1/metadata.txt:qgisMinimumVersion=2.0
        test_plugin_2/metadata.txt:qgisMinimumVersion=2.14
        test_plugin_3/metadata.txt:qgisMinimumVersion=2.0
        test_plugin_4/metadata.txt:qgisMinimumVersion=2.16
        test_plugin_5/metadata.txt:qgisMinimumVersion=2.1
        test_plugin_5/metadata.txt:qgisMaximumVersion=2.3

        test_plugin_1/metadata.txt:version=0.1
        test_plugin_2/metadata.txt:version=0.1
        test_plugin_3/metadata.txt:version=0.1
        test_plugin_4/metadata.txt:version=0.1
        test_plugin_5/metadata.txt:version=0.1

        """
        for i in range(1, 6):
            self.load_from_zip(i)

        def _check_key(i, version):
            key = Plugin.make_key('Test Plugin %s' % i, '0.1' )
            return key in [p.key for p in Plugin.all(version=version)]

        self.assertTrue(_check_key(1, '2.0'))
        self.assertTrue(_check_key(1, '2.99'))
        self.assertFalse(_check_key(1, '3.0'))
        self.assertFalse(_check_key(1, '1.9'))

        self.assertFalse(_check_key(2, '2.0'))
        self.assertTrue(_check_key(2, '2.14'))
        self.assertTrue(_check_key(2, '2.99'))
        self.assertFalse(_check_key(2, '3.0'))
        self.assertFalse(_check_key(2, '1.9'))

        self.assertFalse(_check_key(5, '2.0'))
        self.assertTrue(_check_key(5, '2.1'))
        self.assertTrue(_check_key(5, '2.2'))
        self.assertTrue(_check_key(5, '2.3'))
        self.assertFalse(_check_key(5, '2.4'))
        self.assertFalse(_check_key(5, '2.99'))
        self.assertFalse(_check_key(5, '3.0'))
        self.assertFalse(_check_key(5, '1.9'))

if __name__ == '__main__':
    unittest.main()
