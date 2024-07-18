
import unittest   # The test framework
from src.dphelper.helper import DPHelper

class TestDPHelperProxy(unittest.TestCase):
   
    def test_default_api(self):
        dphelper = DPHelper(
            is_verbose=True,
            proxy_provider=None,
        )
        www = 'https://dphelper.dataplatform.lt'
        html = dphelper.from_url(www)
        self.assertEqual(html, '{"Hello_from":"backend"}')

if __name__ == '__main__':
    unittest.main()
