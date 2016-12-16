# -*- coding: utf-8 -*-
#
# (c) 2016 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
Test the main application
Author: Alessandro Pasotti

"""
import unittest
from lxml import etree
from plugins_admin.plugin_exceptions import *
from .utils import BaseTest

class MainTestCase(BaseTest):


    def test_xml(self):
        """Check plugins returned by filtered XML"""
        for i in range(1, 6):
            self.load_from_zip(i)

        def _check_key(key, version):
            response = self.open_with_auth('/plugins.xml?qgis=%s' % version, method='GET')
            xml = etree.fromstring(response.data)
            result = [e.attrib['name'] for e in xml.xpath('//pyqgis_plugin')]
            return "Test Plugin %s" % key in result

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
