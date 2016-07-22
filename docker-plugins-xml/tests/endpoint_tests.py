#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 endpoint_tests.py

 Performs GET calls on a test repository endpoint loaded
 with the test plugins as explained in the README.md


 Test matrix
 plugin      auth required
 1           no
 2           no
 3           yes
 4           no

Tested Authentication methods:
- HTTP Basic with username and password method GET


                             -------------------
        begin                : 2016-07-18
        git sha              : $Format:%H$
        copyright            : (C) 2016 by
                               Alessandro Pasotti/Boundless Spatial Inc.
        email                : apasotti@boundlessgeo.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import sys
import os

import unittest
import urllib
import urllib2
import base64

USERNAME = 'user'
PASSWORD = 'password'
DEV_USERNAME = 'dev'
DEV_PASSWORD = 'password'

XML_ENDPOINT = os.environ.get('XML_ENDPOINT', 'https://qgis.boundless.test/plugins/')
XML_DEV_ENDPOINT = os.environ.get('XML_DEV_ENDPOINT', 'https://qgis-dev.boundless.test/plugins/')


class TestAuthBase(unittest.TestCase):

    _tokens_cache = {}

    def _get_download_ur(self, plugin_name, requires_auth=False):
        """Overrideable since -dev neds extra steps"""
        return self.endpoint + '/packages' + ('-auth' if requires_auth else '') + '/' + plugin_name + '.zip'

    def _do_post(self, url, requires_auth=True, values={}, headers={}):
        """
        Make a POST request, turns into GET if not requires auth
        (nginx does not support POST on static files)
        """
        if not requires_auth:
            return self._do_get(url, requires_auth, values, headers)
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, headers)
        return urllib2.urlopen(req)

    def _do_get(self, url, requires_auth=True, values={}, headers={}):
        """
        Make a GET request
        """
        req = urllib2.Request(url)
        for n, v in headers.iteritems():
            req.add_header(n, v)
        return urllib2.urlopen(req)

    def _http_basic_header(self, username, password):
        """
        Add the header for HTTP Basic
        """
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
        return {"Authorization": "Basic %s" % base64string}



class TestAuthGET(TestAuthBase):
    """
    HTTP Basic with username and password method POST
    """
    endpoint = XML_ENDPOINT
    username = USERNAME
    password = PASSWORD
    xml = None

    def _get_download_ur(self, plugin_name, requires_auth=False):
        """Get it from XML"""
        if self.xml is None:
            import xml.etree.ElementTree as ET
            self.xml = ET.fromstring(self._do_get(self.endpoint + 'plugins.xml').read())
        # Search the plugins name and get the URL
        return [p for p in self.xml.findall('.//pyqgis_plugin') if p.find('file_name').text.find(plugin_name)!= -1][0].find('download_url').text

    def _do_test(self, url, username=None, password=None, requires_auth=True, values={}):
        headers = {}
        if requires_auth:
            headers = self._http_basic_header(username, password)
        return self._do_get(url, requires_auth, values, headers)

    def test_noAuthRequired(self):
        """
        Test a valid request for a plugin that:
        - do not require authentication
        """
        response = self._do_test(self._get_download_ur('test_plugin_1.0.1'),
                                 requires_auth=False)
        self.assertGreater(len(response.read()), 4800)
        self.assertLess(len(response.read()), 5000)
        self.assertEqual(response.getcode(), 200)

    def test_ValidAuthNoAuthRequired(self):
        """
        Test a valid auth request for a plugin that:
        - do not require authentication
        """
        response = self._do_test(self._get_download_ur('test_plugin_1.0.1'),
                                 self.username, self.password,
                                 requires_auth=False)
        self.assertGreater(len(response.read()), 4800)
        self.assertLess(len(response.read()), 5000)
        self.assertEqual(response.getcode(), 200)


    def test_WrongAuthNoRoleRequired(self):
        """
        Test that a wrong auth request for a plugin that
        - requires authentication
        - requires no role
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_3.0.1',  True))
        the_exception = cm.exception
        self.assertEqual(the_exception.msg.upper(), 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)
        # Wrong username and password
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_3.0.1',  True),
                                     'wrong_username', 'wrong_password')
        the_exception = cm.exception
        self.assertEqual(the_exception.msg.upper(), 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)

    def test_ValidAuthNoRoleRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - requires no role
        """
        response = self._do_test(self._get_download_ur('test_plugin_3.0.1',  True),
                                 self.username, self.password)
        self.assertGreater(len(response.read()), 5000)
        self.assertEqual(response.getcode(), 200)


class TestAuthGET_Dev(TestAuthGET):
    """
    HTTP Basic with username and password method POST
    """
    endpoint = XML_DEV_ENDPOINT
    username = DEV_USERNAME
    password = DEV_PASSWORD



if __name__ == '__main__':
    unittest.main()
