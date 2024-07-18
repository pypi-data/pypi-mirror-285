
import unittest   # The test framework
from src.dphelper.helper import DPHelper


class TestDPHelperService(unittest.TestCase):
 
    def test_default_api(self):
        dphelper = DPHelper()
        self.assertEqual(dphelper.get_backend_url(), 'https://dphelper.dataplatform.lt')

    def test_api(self):
        dphelper = DPHelper(backend_url='https://dphelper.dataplatform.lt')
        greeting = dphelper.get_backend_greeting()
        self.assertEqual(greeting, 'backend')
        self.assertEqual(dphelper.get_backend_url(), 'https://dphelper.dataplatform.lt')

    def test_legacy_api(self):
        dphelper = DPHelper(backend_url='https://api.dataplatform.lt')
        greeting = dphelper.get_backend_greeting()
        self.assertEqual(greeting, 'backend')
        self.assertEqual(dphelper.get_backend_url(), 'https://api.dataplatform.lt')

    def test_dp_id_old(self):
        dphelper = DPHelper(backend_url='https://api.dataplatform.lt')
        self.assertEqual(dphelper.get_dp_url(), 'https://api.dataplatform.lt')
      
    def test_dp_id_new(self):
        dphelper = DPHelper(backend_url='https://dphelper.dataplatform.lt')
        self.assertEqual(dphelper.get_dp_url(), 'https://api.dataplatform.lt')

if __name__ == '__main__':
    unittest.main()
