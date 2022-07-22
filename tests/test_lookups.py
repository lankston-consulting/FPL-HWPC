import pytest
import unittest
import sys

from hwpccalc import model_data


class TestLookups(unittest.TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)
        sys.path.append("../")
        self.md = model_data.ModelData()

    def test_primary_product_to_timber_product(self):
        x = self.md.primary_product_to_timber_product(1)
        self.assertEqual(x, 1)
        y = self.md.primary_product_to_timber_product(11)
        self.assertEqual(y, 2)

    def test_end_use_to_timber_product(self):
        x = self.md.end_use_to_timber_product(2)
        self.assertEqual(x, 1)
        y = self.md.end_use_to_timber_product(60)
        self.assertEqual(y, 2)

    def test_end_use_to_primary_product(self):
        x = self.md.end_use_to_primary_product(1)
        self.assertEqual(x, 1)
        y = self.md.end_use_to_primary_product(2)
        self.assertEqual(y, 2)


if __name__ == "__main__":
    unittest.main()
