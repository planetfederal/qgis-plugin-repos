import os
import unittest
import tempfile
from plugins_admin.plugin import Plugin
from plugins_admin import main
from plugins_admin.plugin_exceptions import *

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

class MainTestCase(unittest.TestCase):

    def setUp(self):
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
