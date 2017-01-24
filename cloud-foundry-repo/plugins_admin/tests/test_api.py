# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
Test the API
Author: Alessandro Pasotti

"""
import os
import unittest
import base64
from flask import json
from plugins_admin.plugin import Plugin
from plugins_admin.plugin_exceptions import *
from cStringIO import StringIO
from plugins_admin.validator import validator
from .utils import BaseTest, DATA_DIR


class APITestCase(BaseTest):

    def test_api_get_metadata(self):
        plugin = self.load_from_zip()
        response = self.open_with_auth('/rest/metadata/%s/%s' % (plugin.key, 'version'), method='GET')
        self.assertEqual(plugin.version, json.loads(response.data)['version'])

    def test_api_change_version_metadata(self):
        plugin = self.load_from_zip()
        response = self.open_with_auth('/rest/metadata/%s/%s' % (plugin.key, 'version'), method='POST', data='0.123')
        self.assertNotEqual(plugin.version, json.loads(response.data)['version'])
        response = self.open_with_auth('/rest/metadata/%s/%s' % (plugin.make_key(plugin.name, '0.123'), 'version'), method='GET')
        self.assertEqual('0.123', json.loads(response.data)['version'])
        # Check with the new key since version has changed
        response = self.open_with_auth('/rest/metadata/%s/%s' % (plugin.key, 'version'), method='GET')
        self.assertEqual(response.status_code, 404)

    def test_api_new_metadata(self):
        plugin = self.load_from_zip()
        response = self.open_with_auth('/rest/metadata/%s/%s' % (plugin.key, 'xyz'), method='POST', data='zyx')
        self.assertEqual('zyx', json.loads(response.data)['xyz'])
        # Get the package and check the zip file
        response = self.open_with_auth('/rest/package/%s' % plugin.key, method='GET')
        package = base64.decodestring(json.loads(response.data).values()[0])
        self.assertNotEqual(package, open(os.path.join(DATA_DIR, 'test_plugin_1.zip')).read())
        metadata = dict(validator(StringIO(package)))
        self.assertEqual(metadata['xyz'], 'zyx')

    def test_api_get_package(self):
        plugin = self.load_from_zip()
        response = self.open_with_auth('/rest/package/%s' % plugin.key, method='GET')
        package = base64.decodestring(json.loads(response.data).values()[0])
        self.assertEqual(package, open(os.path.join(DATA_DIR, 'test_plugin_1.zip')).read())

    def test_api_post_package(self):
        data = open(os.path.join(DATA_DIR, 'test_plugin_1.zip')).read()
        response = self.open_with_auth('/rest/package/', method='POST', data=data)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['result'], 'success')
        self.assertEqual(response_data['plugin']['name'], u'Test Plugin 1')
        key = Plugin.make_key(response_data['plugin']['name'], response_data['plugin']['version'])

        # Loopback
        response = self.open_with_auth('/rest/package/%s' % key, method='GET')
        package = base64.decodestring(json.loads(response.data).values()[0])
        self.assertEqual(package, open(os.path.join(DATA_DIR, 'test_plugin_1.zip')).read())
        # Get the package and check the zip file
        metadata = dict(validator(StringIO(package)))
        self.assertEqual(metadata['name'], response_data['plugin']['name'])
        self.assertEqual(metadata['version'], response_data['plugin']['version'])
        self.assertEqual(metadata['author'], response_data['plugin']['author'])

    def test_api_post_invalid_package(self):
        data = open(os.path.join(DATA_DIR, 'test_plugin_invalid.zip')).read()
        response = self.open_with_auth('/rest/package/', method='POST', data=data)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['result'], 'error')

    def test_plugins_list(self):
        self.load_from_zip()
        self.load_from_zip(2)
        response = self.open_with_auth('/rest/plugins', method='GET')
        plugins = dict(json.loads(response.data)['plugins'].items())
        for p in Plugin.all():
            self.assertIn(p.key, plugins.keys())
            for k, v in p.metadata.items():
                self.assertEqual(getattr(p, k), v)

    def test_api_delete_package(self):
        plugin = self.load_from_zip()
        # Delete it
        response = self.open_with_auth('/rest/package/%s' % plugin.key, method='DELETE')
        self.assertEqual(json.loads(response.data)['result'], 'success')
        # Check if it's been deleted for real
        def load_deleted():
            Plugin(plugin.key)
        self.assertRaises(DoesNotExist, load_deleted)



if __name__ == '__main__':
    unittest.main()
