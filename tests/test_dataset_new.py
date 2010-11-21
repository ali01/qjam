import unittest
import numpy
from . import fixture
from qjam.dataset_new import DataSet

class TestDataSet(unittest.TestCase):
    pass

class TestListDataSet(unittest.TestCase):
  def test_len(self):
    self.assertEqual(4, len(DataSet(range(0,120))))
    self.assertEqual(120, len(DataSet(range(0,120), slice_size=1)))
    self.assertEqual(24, len(DataSet(range(0,120), slice_size=5)))

  def test_getitem(self):
    ds = DataSet(range(0,120))
    self.assertEqual(range(0, 30), ds[0])
    self.assertEqual(range(30, 60), ds[1])
    self.assertEqual(range(60, 90), ds[2])
    self.assertEqual(range(90, 120), ds[3])
    self.assertEqual([range(30, 60), range(60, 90)], ds[1:3])
    ds = DataSet(range(0,120), slice_size=1)
    self.assertEqual([0], ds[0])
    self.assertEqual([119], ds[119])
    self.assertEqual([[10], [11], [12]], ds[10:13])

  def test_slices(self):
    ds = DataSet(range(0,120))
    self.assertEqual(range(0, 30), ds.slice(0))
    self.assertEqual(range(30, 60), ds.slice(1))
    self.assertEqual(range(60, 90), ds.slice(2))
    self.assertEqual(range(90, 120), ds.slice(3))
    ds = DataSet(range(0,120), slice_size=1)
    self.assertEqual([0], ds.slice(0))
    self.assertEqual([119], ds.slice(119))


class TestNumpyMatrixDataSet(unittest.TestCase):
  def test_len(self):
    x = numpy.matrix("[%s]" % ("1 2;3 4;5 6;7 8;9 10;" * 10).strip(';'))
    self.assertEqual(10, len(DataSet(x)))
    self.assertEqual(50, len(DataSet(x, slice_size=1)))
    self.assertEqual(17, len(DataSet(x, slice_size=3)))

  def test_getitem(self):
    def mat_repeated(repeated):
      basic = "1 2;3 4;5 6;7 8;9 10;"
      return numpy.matrix("[%s]" % (basic * repeated).strip(';'))

    def mat_repeated_list(repeated, size): # for python slices
      ret = []
      for i in range(0, size):
        ret.append(mat_repeated(repeated))
      return ret

    def mat_list_equals(list1, list2): # for python slices
      for i in range(0, len(list1)):
        if (list1[i] != list2[i]).all():
          return False
      return True

    ds = DataSet(mat_repeated(10))
    self.assertTrue((mat_repeated(1) == ds[0]).all())
    self.assertTrue((mat_repeated(1) == ds[1]).all())
    self.assertTrue((mat_repeated(1) == ds[2]).all())
    self.assertTrue(mat_list_equals(mat_repeated_list(1, 4), ds[1:5]))

    ds = DataSet(mat_repeated(10), slice_size=10)
    self.assertTrue((mat_repeated(2) == ds[0]).all())
    self.assertTrue(mat_list_equals(mat_repeated_list(2, 3), ds[0:4]))

    ds = DataSet(mat_repeated(10), slice_size=100)
    self.assertTrue((mat_repeated(10) == ds[0]).all())
    self.assertTrue(mat_list_equals(mat_repeated_list(10, 1), ds[0:1]))

  def test_slices(self):
    def mat_repeated(repeated):
      basic = "1 2;3 4;5 6;7 8;9 10;"
      return numpy.matrix("[%s]" % (basic * repeated).strip(';'))

    ds = DataSet(mat_repeated(10))
    self.assertTrue((mat_repeated(1) == ds.slice(0)).all())
    self.assertTrue((mat_repeated(1) == ds.slice(1)).all())
    self.assertTrue((mat_repeated(1) == ds.slice(2)).all())

    ds = DataSet(mat_repeated(10), slice_size=10)
    self.assertTrue((mat_repeated(2) == ds.slice(0)).all())

    ds = DataSet(mat_repeated(10), slice_size=100)
    self.assertTrue((mat_repeated(10) == ds.slice(0)).all())

