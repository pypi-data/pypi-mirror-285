
import unittest   # The test framework
from src.dphelper.helper import DPHelper

class TestDPHelperParsers(unittest.TestCase):

    def test_parse_real_estate_listing(self):
        dphelper = DPHelper()
        self.assertEqual(dphelper.parse_rows(
            ['id', 'floor', 'area', 'rooms', 'price'],
            [['A1', '2', '50.44', '2', '100.000']]
        ), [{'area': 50.44, 'floor': 2, 'id': 'a1', 'price': 100000.0, 'rooms': 2}])

    def test_parse_id(self):
        dphelper = DPHelper()
        self.assertEqual(dphelper.parse_rows(['id'], [['A1']]), [{'id': 'a1'}])
        self.assertEqual(dphelper.parse_rows(['id'], [['a 1']]), [{'id': 'a1'}])

    def test_parse_price(self):
        dphelper = DPHelper()
        self.assertEqual(dphelper.parse_rows(['price'], [['100.000,00']]), [{'price': 100000}])
        self.assertEqual(dphelper.parse_rows(['price'], [['40.23']]), [{'price': 40.23}])

    def test_parse_value(self):
        dphelper = DPHelper()
        self.assertEqual(dphelper.parse_value('100.000,00', 'price'), 100000)

    def test_tansform_map(self):
        dphelper = DPHelper()     
        schema_map = {"kaina": "price", "plotas": "area"}
        data = [{"kaina": 1, "plotas": 2}]
        self.assertEqual(dphelper.transform_map(schema_map, data), [{"price": 1, "area": 2}])

if __name__ == '__main__':
    unittest.main()
