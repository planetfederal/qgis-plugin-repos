#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 endpoint_tests.py

 Test matrix
 plugin      auth required       min role
 1           no                  -
 2           yes                 DesktopBasic
 3           yes                 -
 4           yes                 DesktopEnterprise


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


XML_ENDPOINT='https://qgis.boundless.test/plugins/'

try:
    DESKTOP_ROLE_ACCOUNTS = {
      'Registered': (env['QGIS_FREE_USERNAME'], env['QGIS_FREE_PASSWORD']),
      'DesktopBasic': (env['QGIS_BASIC_USERNAME'], env['QGIS_BASIC_PASSWORD']),
      'DesktopEnterprise' : (env['QGIS_ENTERPRISE_USERNAME'], env['QGIS_ENTERPRISE_PASSWORD']),
    }
except KeyError:
    env_err()


class TestAuth0(unittest.TestCase):

    def _do_post(self, url, values={}, headers={}):
        """
        Make a post request
        """
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, headers)
        return urllib2.urlopen(req)

    def _do_get(self, url, headers={}):
        """
        Make a get request
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

    def test_noAuthRequired(self):
        """
        Test a valid request for a plugin that:
        - do not require authentication
        """
        response = self._do_get(XML_ENDPOINT + '/packages/test_plugin_1.0.1.zip')
        self.assertEqual(len(response.read()), 4880)
        self.assertEqual(response.getcode(), 200)

    def test_ValidAuthNoAuthRequired(self):
        """
        Test a valid auth request for a plugin that:
        - do not require authentication
        """
        response = self._do_get(XML_ENDPOINT + '/packages/test_plugin_1.0.1.zip',
                                headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['DesktopBasic']))
        self.assertEqual(len(response.read()), 4880)
        self.assertEqual(response.getcode(), 200)

    def test_WrongAuthDesktopBasicRequired(self):
        """
        Test that a wrong auth request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_2.0.1.zip')
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)

    def test_ValidAuthDesktopBasicRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_2.0.1.zip',
                                headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['DesktopBasic']))
        self.assertEqual(len(response.read()), 5189)
        self.assertEqual(response.getcode(), 200)

    def test_WrongAuthNoRoleRequired(self):
        """
        Test that a wrong auth request for a plugin that
        - requires authentication
        - requires no role
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_3.0.1.zip')
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)
        # Wrong username and password
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_3.0.1.zip',
                                    headers=self._http_basic_header('wrong_username', 'wrong_password'))
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)

    def test_ValidAuthNoRoleRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - requires no role
        """
        response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_3.0.1.zip',
                                headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['DesktopBasic']))
        self.assertEqual(len(response.read()), 5082)
        self.assertEqual(response.getcode(), 200)


    def test_WrongAuthDesktopBasicRequired(self):
        """
        Test that a wrong auth request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_2.0.1.zip')
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)
        # Wrong username and password
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_2.0.1.zip',
                                    headers=self._http_basic_header('wrong_username', 'wrong_password'))
        the_exception = cm.exception
        self.assertEqual(the_exception.msg, 'UNAUTHORIZED')
        self.assertEqual(the_exception.getcode(), 401)

    def test_ValidAuthDesktopBasicRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_2.0.1.zip',
                                headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['DesktopBasic']))
        self.assertEqual(len(response.read()), 5189)
        self.assertEqual(response.getcode(), 200)

    def test_ValidAuthWrongRoleDesktopBasicRequired(self):
        """
        Test that a valid auth/wrong role request for a plugin that
        - requires authentication
        - require DesktopBasic authorization
        """
        with self.assertRaises(urllib2.HTTPError) as cm:
            response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_2.0.1.zip',
                                    headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['Registered']))
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
            response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_4.0.1.zip',
                                    headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['DesktopBasic']))
        the_exception = cm.exception
        self.assertEqual(the_exception.getcode(), 403)
        self.assertEqual(the_exception.msg, 'FORBIDDEN')

    def test_ValidAuthDesktopEnterpriseRequired(self):
        """
        Test that a valid auth request for a plugin that
        - requires authentication
        - require DesktopEnterprise authorization
        """
        response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_4.0.1.zip',
                                headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['DesktopEnterprise']))
        self.assertEqual(len(response.read()), 2979)
        self.assertEqual(response.getcode(), 200)

    def test_ValidAuthHigherRoleDesktopBasicRequired(self):
        """
        Test that a valid auth/higher role request for a plugin that
        - requires authentication
        - require DesktopEnterprise authorization
        """
        response = self._do_get(XML_ENDPOINT + 'packages-auth/test_plugin_2.0.1.zip',
                                headers=self._http_basic_header(*DESKTOP_ROLE_ACCOUNTS['DesktopEnterprise']))
        self.assertEqual(len(response.read()), 5189)
        self.assertEqual(response.getcode(), 200)



if __name__ == '__main__':
    unittest.main()
