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
    self.assertEqual(range(0, 30), ds[0].raw_data())
    self.assertEqual(range(30, 60), ds[1].raw_data())
    self.assertEqual(range(60, 90), ds[2].raw_data())
    self.assertEqual(range(90, 120), ds[3].raw_data())
    raw = map(lambda x: x.raw_data(), ds[1:3])
    self.assertEqual([range(30, 60), range(60, 90)], raw)

    ds = DataSet(range(0,120), slice_size=1)
    self.assertEqual([0], ds[0].raw_data())
    self.assertEqual([119], ds[119].raw_data())
    raw = map(lambda x: x.raw_data(), ds[10:13])
    self.assertEqual([[10], [11], [12]], raw)

  def test_slices(self):
    ds = DataSet(range(0,120))
    self.assertEqual(range(0, 30), ds.slice(0).raw_data())
    self.assertEqual(range(30, 60), ds.slice(1).raw_data())
    self.assertEqual(range(60, 90), ds.slice(2).raw_data())
    self.assertEqual(range(90, 120), ds.slice(3).raw_data())
    ds = DataSet(range(0,120), slice_size=1)
    self.assertEqual([0], ds.slice(0).raw_data())
    self.assertEqual([119], ds.slice(119).raw_data())

  def test_hash(self):
    ds1 = DataSet(range(0,120))
    ds2 = DataSet(range(0,120))
    self.assertEqual(ds1.hash(0), ds2.hash(0))
    self.assertEqual(ds1.hash(1), ds2.hash(1))
    self.assertEqual(ds1.hash(2), ds2.hash(2))
    self.assertEqual(ds1.hash(3), ds2.hash(3))
    ds1 = DataSet(range(0,120), slice_size=1)
    ds2 = DataSet(range(0,120), slice_size=1)
    for i in range(0, 120, 10):
      self.assertEqual(ds1.hash(i), ds2.hash(i))


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
    self.assertTrue((mat_repeated(1) == ds[0].raw_data()).all())
    self.assertTrue((mat_repeated(1) == ds[1].raw_data()).all())
    self.assertTrue((mat_repeated(1) == ds[2].raw_data()).all())
    raw = map(lambda x: x.raw_data(), ds[1:5])
    self.assertTrue(mat_list_equals(mat_repeated_list(1, 4), raw))

    ds = DataSet(mat_repeated(10), slice_size=10)
    self.assertTrue((mat_repeated(2) == ds[0].raw_data()).all())
    raw = map(lambda x: x.raw_data(), ds[0:4])
    self.assertTrue(mat_list_equals(mat_repeated_list(2, 3), raw))

    ds = DataSet(mat_repeated(10), slice_size=100)
    self.assertTrue((mat_repeated(10) == ds[0].raw_data()).all())
    raw = map(lambda x: x.raw_data(), ds[0:1])
    self.assertTrue(mat_list_equals(mat_repeated_list(10, 1), raw))

  def test_slices(self):
    def mat_repeated(repeated):
      basic = "1 2;3 4;5 6;7 8;9 10;"
      return numpy.matrix("[%s]" % (basic * repeated).strip(';'))

    ds = DataSet(mat_repeated(10))
    self.assertTrue((mat_repeated(1) == ds.slice(0).raw_data()).all())
    self.assertTrue((mat_repeated(1) == ds.slice(1).raw_data()).all())
    self.assertTrue((mat_repeated(1) == ds.slice(2).raw_data()).all())

    ds = DataSet(mat_repeated(10), slice_size=10)
    self.assertTrue((mat_repeated(2) == ds.slice(0).raw_data()).all())

    ds = DataSet(mat_repeated(10), slice_size=100)
    self.assertTrue((mat_repeated(10) == ds.slice(0).raw_data()).all())

  def test_hash(self):
    x = numpy.matrix("[%s]" % ("1 2;3 4;5 6;7 8;9 10;" * 10).strip(';'))

    for slice_size in [30, 1, 3]:
      ds1 = DataSet(x, slice_size=slice_size)
      ds2 = DataSet(x, slice_size=slice_size)
      self.assertEqual(ds1.hash(), ds2.hash())
      for i in range(0, len(ds1)):
        self.assertEqual(ds1.hash(i), ds2.hash(i))
        slice1 = ds1.slice_with_hash(ds1.hash(i)).raw_data()
        slice2 = ds2.slice_with_hash(ds2.hash(i)).raw_data()
        slice12 = ds1.slice_with_hash(ds2.hash(i)).raw_data()
        slice21 = ds2.slice_with_hash(ds1.hash(i)).raw_data()
        self.assertTrue((slice1 == slice2).all())
        self.assertTrue((slice12 == slice21).all())
        self.assertTrue((slice1 == slice21).all())
