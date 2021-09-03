import pytest
import unittest

from hwpccalc.hwpc.model_data import ModelData as md

class TestLookups(unittest.TestCase):

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        md()
    
    def test_primary_product_to_timber_product(self):
        x = md.primary_product_to_timber_product(1)
        self.assertEqual(x, 1)
        y = md.primary_product_to_timber_product(11)
        self.assertEqual(y, 2)

    def test_end_use_to_timber_product(self):
        x = md.end_use_to_timber_product(2)
        self.assertEqual(x, 1)
        y = md.end_use_to_timber_product(60)
        self.assertEqual(y, 2)

    def test_end_use_to_primary_product(self):
        x = md.end_use_to_primary_product(1)
        self.assertEqual(x, 1)
        y = md.end_use_to_primary_product(2)
        self.assertEqual(y, 2)

if __name__ == '__main__':
    unittest.main()