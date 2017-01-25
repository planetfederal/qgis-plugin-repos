# -*- coding: utf-8 -*-
#
# (c) 2017 Boundless, http://boundlessgeo.com
# This code is licensed under the GPL 2.0 license.
#
"""
Test the main application
Author: Alessandro Pasotti

"""
import os
import unittest
from update_index import process

class MainTestCase(unittest.TestCase):

    def _removeXml(self):
        if os.path.exists(os.path.join(self.data_dir, 'plugins.xml')):
            os.unlink(self.xml_path)

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.xml_path = os.path.join(self.data_dir, 'plugins.xml')
        self.reference_xml_path = os.path.join(self.data_dir, 'plugins_reference.xml')
        self._removeXml()


    def test_xml(self):
        process(self.data_dir, 'https://www.boundlessgeo.com/plugins/download', True)
        self.assertTrue(os.path.exists(self.xml_path))
        xml = open(self.xml_path).read()
        reference_xml = open(self.reference_xml_path).read()
        self.assertEquals(reference_xml, xml)


if __name__ == '__main__':
    unittest.main()
