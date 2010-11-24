import unittest
import numpy
from . import fixture
from qjam.dataset import DataSet

class TestDataSet(unittest.TestCase):
    pass

class TestListDataSet(unittest.TestCase):
    def test_slices(self):
        ds = DataSet([1,2,3,4,5])
        slices = ds.slices(3)
        self.assertEqual([1,2], slices[0])
        self.assertEqual([3,4], slices[1])
        self.assertEqual([5], slices[2])

class TestNumPyMatrixDataSet(unittest.TestCase):
    def test_slices(self):
        x = numpy.array([[1,2],[3,4],[5,6],[7,8],[9,10]])
        ds = DataSet(x)
        slices = ds.slices(3)
        self.assertTrue((numpy.array([[1,2],[3,4]]) == slices[0]).all())
        self.assertTrue((numpy.array([[5,6],[7,8]]) == slices[1]).all())
        self.assertTrue((numpy.array([[9,10]]) == slices[2]).all())
        
