# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
Base test class
Author: Alessandro Pasotti

"""
import os
import unittest
import base64
from plugins_admin.plugin import Plugin
from plugins_admin import main

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

USERNAME = os.getenv("USERNAME", 'admin')
PASSWORD = os.getenv("PASSWORD", 'password')

class BaseTest(unittest.TestCase):
    """Common test functioality"""

    def setUp(self):
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()

    def tearDown(self):
        for p in Plugin.all():
            p.delete(p.key)

    def load_from_zip(self, version=1):
        plugin_path = os.path.join(DATA_DIR, 'test_plugin_%s.zip' % version)
        zip_file = open(plugin_path, 'rb')
        plugin = Plugin.create_from_zip(zip_file)
        self.assertIsNotNone(Plugin(plugin.key))
        return plugin

    def open_with_auth(self, url, method, data=None):
        return self.app.open(url,
            method=method,
            headers={
                'Authorization': 'Basic ' + base64.b64encode(USERNAME + \
                ":" + PASSWORD)
            },
            data=data
        )
