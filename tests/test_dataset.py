import unittest
from . import fixture
from qjam import DataSet

class TestDataSet(unittest.TestCase):
    pass

class TestListDataSet(unittest.TestCase):
    def test_slices(self):
        ds = DataSet([1,2,3,4,5])
        slices = ds.slices(3)
        self.assertEqual([1,2], slices[0])
        self.assertEqual([3,4], slices[1])
        self.assertEqual([5], slices[2])
