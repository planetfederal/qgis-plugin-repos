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
from flask import json, jsonify
from plugins_admin.plugin import Plugin
from plugins_admin import main
from plugins_admin.plugin_exceptions import *
from cStringIO import StringIO
from plugins_admin.validator import validator

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

USERNAME = os.getenv("USERNAME", 'admin')
PASSWORD = os.getenv("PASSWORD", 'password')

class APITestCase(unittest.TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()

    def tearDown(self):
        for p in Plugin.all():
            p.delete(p.key)

    def open_with_auth(self, url, method, data=None):
        return self.app.open(url,
            method=method,
            headers={
                'Authorization': 'Basic ' + base64.b64encode(USERNAME + \
                ":" + PASSWORD)
            },
            data=data
        )

    def load_from_zip(self, version=1):
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_%s.zip'  % version)
        zip_file = open(plugin_path, 'rb')
        plugin = Plugin.create_from_zip(zip_file)
        self.assertIsNotNone(Plugin(plugin.key))
        return plugin

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
        plugin = self.load_from_zip()
        response = self.open_with_auth('/rest/package/%s' % plugin.key, method='GET')
        package = base64.decodestring(json.loads(response.data).values()[0])
        self.assertEqual(package, open(os.path.join(DATA_DIR, 'test_plugin_1.zip')).read())
        # Get the package and check the zip file
        response = self.open_with_auth('/rest/package/%s' % plugin.key, method='GET')
        package = base64.decodestring(json.loads(response.data).values()[0])
        self.assertEqual(package, open(os.path.join(DATA_DIR, 'test_plugin_1.zip')).read())
        metadata = dict(validator(StringIO(package)))
        self.assertEqual(metadata['name'], plugin.name)
        self.assertEqual(metadata['version'], plugin.version)
        self.assertEqual(metadata['author'], plugin.author)

    def test_plugins_list(self):
        plugin = self.load_from_zip()
        plugin = self.load_from_zip(2)
        response = self.open_with_auth('/rest/plugins', method='GET')
        plugins = dict(json.loads(response.data)['plugins'].items())
        for p in Plugin.all():
            self.assertIn(p.key, plugins.keys())
            for k, v in p.metadata.items():
                self.assertEqual(getattr(p, k), v)



if __name__ == '__main__':
    unittest.main()
