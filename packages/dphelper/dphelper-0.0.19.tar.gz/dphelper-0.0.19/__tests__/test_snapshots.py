
import unittest   # The test framework
from src.dphelper.helper import DPHelper

class TestDPHelperSnapshots(unittest.TestCase):
   
    def test_test_basic(self):
        dphelper = DPHelper()
        response_full = dphelper.snapshot.get_latest(by_challenge_id=140) 
        data_result = response_full.result
        self.assertGreater(len(data_result), 0)
  
if __name__ == '__main__':
    unittest.main()
