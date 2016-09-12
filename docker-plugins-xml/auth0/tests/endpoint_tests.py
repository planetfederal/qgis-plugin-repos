#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 endpoint_tests.py

 Performs GET/POST and token tests on a test repository endpoint loaded
 with the test plugins as explained in the README.md

 WARNING: the wrong credentials tests must be disabled (skipped) to avoid Auth0
          IP and account locks.

 Test matrix
 plugin      auth required       role
 1           no                  -
 2           yes                 DesktopBasic,DesktopEnterprise
 3           yes                 -
 4           yes                 DesktopEnterprise

Tested Authentication methods:
- HTTP Basic with username and password method GET
- HTTP Basic with username and password method POST
- Authorization Request Header Field access token (Bearer) method POST
- Access token passed on the query string as `access_token` method GET
- Form-Encoded Body Parameter access token passed as `access_token` method POST


                             -------------------
        begin                : 2016-06-28
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

import json
import unittest
import urllib
import urllib2
import base64


env = None
AUTH0_ENV = os.path.join(os.path.expanduser("~"), '.auth0.env')

def env_err():
    """Print the env error message and die"""
    print("A .env file with sample accounts is needed to run this tests.")
    print("""The .env must contain the Auth0 configuration and:
QGIS_FREE_USERNAME=********* # with Registered permissions
QGIS_FREE_PASSWORD=*********
QGIS_BASIC_USERNAME=******** # with DesktopBasic and Suite permissions
QGIS_BASIC_PASSWORD=********
QGIS_ENTERPRISE_USERNAME=*** # with DesktopEnterprise and Suite permissions
QGIS_ENTERPRISE_PASSWORD=***
     """)
    sys.exit(1)

try:
    from dotenv import Dotenv
    if os.path.exists(AUTH0_ENV):
        env = Dotenv(AUTH0_ENV)
    else:
        env = Dotenv('../.env')
except IOError:
    env_err()


XML_ENDPOINT = os.environ.get('XML_ENDPOINT', 'https://qgis.boundless.test/plugins/')
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'https://qgis.boundless.test/api/')

try:
    DESKTOP_ROLE_ACCOUNTS = {
      'Registered': (env['QGIS_FREE_USERNAME'], env['QGIS_FREE_PASSWORD']),
      'DesktopBasic': (env['QGIS_BASIC_USERNAME'], env['QGIS_BASIC_PASSWORD']),
      'DesktopEnterprise' : (env['QGIS_ENTERPRISE_USERNAME'], env['QGIS_ENTERPRISE_PASSWORD']),
    }
except KeyError:
    env_err()


class TestAuth0Base(unittest.TestCase):

    _tokens_cache = {}
    endpoint = XML_ENDPOINT
    api_endpoint = API_ENDPOINT
    xml = None

    def _get_download_ur(self, plugin_name, requires_auth=False):
        """Get it from XML"""
        if self.xml is None:
            import xml.etree.ElementTree as ET
            self.xml = ET.fromstring(self._do_get(self.endpoint + 'plugins.xml').read())
        # Search the plugins name and get the URL
        return [p for p in self.xml.findall('.//pyqgis_plugin') if p.find('file_name').text.find(plugin_name) != -1][0].find('download_url').text


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

    def _http_bearer_header(self, access_token):
        """
        Add the Authorization: Bearer header
        """
        return {"Authorization": "Bearer %s" % access_token}

    def _get_access_token(self, url, username=None, password=None):
        """Return the access_token"""
        try:
            access_token = self._tokens_cache['%s%s' % (username, password)]
        except KeyError:
            headers = self._http_basic_header(username, password)
            response = self._do_post(url, requires_auth=True, headers=headers)
            access_token = response.headers['X-Access-Token']
            self._tokens_cache['%s%s' % (username, password)] = access_token
        return access_token


class TestAuth0GET(TestAuth0Base):
    """
    HTTP Basic with username and password method POST
    """

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
                                 *DESKTOP_ROLE_ACCOUNTS['DesktopBasic'],
                                 requires_auth=False)
        self.assertGreater(len(response.read()), 4800)
        self.assertLess(len(response.read()), 5000)
        self.assertEqual(response.getcode(), 200)

    def test_ValidAuthUserProfile(self):
        """
        Test a valid auth request for a user profile
        """
        response = self._do_test(self.api_endpoint + 'user_profile',
                                 *DESKTOP_ROLE_ACCOUNTS['DesktopBasic'],
                                 requires_auth=True)
        self.assertEqual(response.getcode(), 200)
        text = response.read()
        response_j = json.loads(text)
        self.assertTrue(response_j.get('SiteRole').find('DesktopBasic') != -1)

    def test_ValidAuthUserRoles(self):
        """
        Test a valid auth request for a user roles
        """
        response = self._do_test(self.api_endpoint + 'user_roles',
                                 *DESKTOP_ROLE_ACCOUNTS['DesktopBasic'],
                                 requires_auth=True)
        self.assertEqual(response.getcode(), 200)
        text = response.read()
        response_j = json.loads(text)
        self.assertEquals(response_j,  [u'Suite', u'DesktopBasic'])

    @unittest.skip("Auth0 locks")
    def test_WrongAuthNoRoleRequired(self):
        """
        Test that a wrong auth request for a plugin that
        - requires authentication
        - requires no role
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_3.0.1'))
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)
        # Wrong username and password
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_3.0.1'),
                                     'wrong_username', 'wrong_password')
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)

    def test_ValidAuthNoRoleRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - requires no role
        """
        response = self._do_test(self._get_download_ur('test_plugin_3.0.1'),
                                 *DESKTOP_ROLE_ACCOUNTS['DesktopBasic'])
        self.assertGreater(len(response.read()), 5000)
        self.assertEqual(response.getcode(), 200)

    @unittest.skip("Auth0 locks")
    def test_WrongAuthDesktopBasicRequired(self):
        """
        Test that a wrong auth request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_2.0.1'))
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)
        # Wrong username and password
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_2.0.1'),
                                     'wrong_username', 'wrong_password')
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)

    def test_ValidAuthDesktopBasicRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        response = self._do_test(self._get_download_ur('test_plugin_2.0.1'),
                                 *DESKTOP_ROLE_ACCOUNTS['DesktopBasic'])
        self.assertGreater(len(response.read()), 5000)
        self.assertEqual(response.getcode(), 200)


    def test_ValidAuthWrongRoleDesktopBasicRequired(self):
        """
        Test that a valid auth/wrong role request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_2.0.1'),
                                     *DESKTOP_ROLE_ACCOUNTS['Registered'])
        the_exception = cm.exception
        self.assertEqual(the_exception.getcode(), 403)
        self.assertEqual(the_exception.msg, 'FORBIDDEN')

    def test_ValidAuthWrongRoleDesktopEnterpriseRequired(self):
        """
        Test that a valid auth/wrong role request for a plugin that
        - requires authentication
        - require DesktopEnterprise authorization
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_test(self._get_download_ur('test_plugin_4.0.1'),
                                     *DESKTOP_ROLE_ACCOUNTS['DesktopBasic'])
        the_exception = cm.exception
        self.assertEqual(the_exception.getcode(), 403)
        self.assertEqual(the_exception.msg, 'FORBIDDEN')

    def test_ValidAuthDesktopEnterpriseRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - require DesktopEnterprise authorization
        """
        response = self._do_test(self._get_download_ur('test_plugin_4.0.1'),
                                 *DESKTOP_ROLE_ACCOUNTS['DesktopEnterprise'])
        self.assertGreater(len(response.read()), 2900)
        self.assertLess(len(response.read()), 3000)
        self.assertEqual(response.getcode(), 200)

    def test_ValidAuthHigherRoleDesktopBasicRequired(self):
        """
        Test that a valid auth/role request for a plugin that
        - requires authentication
        - require DesktopBasic or DesktopEnterprise authorization
        """
        response = self._do_test(self._get_download_ur('test_plugin_2.0.1'),
                                 *DESKTOP_ROLE_ACCOUNTS['DesktopEnterprise'])
        self.assertGreater(len(response.read()), 5000)
        self.assertEqual(response.getcode(), 200)


class TestAuth0POST(TestAuth0GET):
    """
    HTTP Basic with username and password method POST
    """

    def _do_test(self, url, username=None, password=None, requires_auth=True, values={}):
        headers = {}
        if not requires_auth or username is None or password is None:
            return self._do_get(url, requires_auth=requires_auth)
        headers = self._http_basic_header(username, password)
        return self._do_post(url, requires_auth, values, headers)


class TestAuth0Bearer(TestAuth0GET):
    """
    Authorization Request Header Field access token (Bearer) method POST
    """

    def _do_test(self, url, username=None, password=None, requires_auth=True, values={}):
        # Get the token
        headers = {}
        if requires_auth and username is not None and password is not None:
            headers = self._http_bearer_header(self._get_access_token(url, username, password))
            return self._do_post(url, requires_auth, values, headers)
        else: # for clarity
            return self._do_get(url, requires_auth, values, headers)


class TestAuth0GETQueryString(TestAuth0GET):
    """
    Access token passed on the query string as `access_token` method GET
    """
    def _do_test(self, url, username=None, password=None, requires_auth=True, values={}):
        headers = {}
        if requires_auth and username is not None and password is not None:
            url = '%s?access_token=%s' % (url, self._get_access_token(url, username, password))
        return self._do_get(url, requires_auth, values, headers)


class TestAuth0POSTAccessToken(TestAuth0GET):
    """
    Form-Encoded Body Parameter access token passed as `access_token` method POST
    """
    def _do_test(self, url, username=None, password=None, requires_auth=True, values={}):
        if requires_auth and username is not None and password is not None:
            values = {'access_token': self._get_access_token(url, username, password)}
        return self._do_post(url, requires_auth, values)


if __name__ == '__main__':
    unittest.main()
