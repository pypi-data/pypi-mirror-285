import unittest
from pygimp.pygimp_core import PyGIMP

class TestPyGIMP(unittest.TestCase):

    def test_load_config(self):
        pygimp = PyGIMP(config_file="gimp_script_config.json")
        config = pygimp.load_config()
        self.assertIsNotNone(config)
        self.assertIn("arguments", config)
        self.assertIn("script_path", config)
