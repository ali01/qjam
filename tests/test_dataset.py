import unittest
import numpy
from . import fixture
from qjam.dataset_new import DataSet
from qjam.dataset_new import NumpyMatrixFileDataSet as MatFileDataSet

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
        slice1 = ds1.slice_from_hash(ds1.hash(i)).raw_data()
        slice2 = ds2.slice_from_hash(ds2.hash(i)).raw_data()
        slice12 = ds1.slice_from_hash(ds2.hash(i)).raw_data()
        slice21 = ds2.slice_from_hash(ds1.hash(i)).raw_data()
        self.assertTrue((slice1 == slice2).all())
        self.assertTrue((slice12 == slice21).all())
        self.assertTrue((slice1 == slice21).all())

# first [6x3]
MAT1 = numpy.matrix('''[3.4344572e-001  2.0327842e-001  2.7077097e-001;
                        8.3287853e-001  3.6993021e-001  6.5773137e-002;
                        8.4007967e-001  5.3165346e-001  5.5266935e-002;
                       -8.8066019e-002  3.4174287e-001  4.2201486e-001;
                       -4.5991808e-001 -5.2611965e-001 -3.7081185e-001;
                        8.1759316e-001  3.0006123e-001 -6.7361891e-002]''')


# second [6x3] at line 2000 (use with 20, 50, 100)
MAT2 = numpy.matrix('''[-1.2422224e-001  7.6260357e-003 -1.9271058e-001;
                        -2.2417808e-002 -3.3010733e-001 -6.3260758e-001;
                         1.2305029e-001 -1.9470690e-001 -6.9714034e-001;
                         6.6523403e-002 -5.6120288e-002 -5.5267900e-001;
                        -8.8423062e-003 -9.2184268e-002 -2.8839281e-001;
                         3.4075595e-002 -9.2937440e-002 -2.7906180e-003]''')


# third [6x3] at line 1485 (to use with 99)
MAT3 = numpy.matrix('''[-7.3648691e-002 -5.8656108e-002 -1.9319049e-001;
                        -7.9926804e-002 -1.2794739e-001 -2.4159192e-001;
                         4.8503876e-002 -3.1440929e-002 -1.2683442e-001;
                         1.5148732e-001  2.0549977e-002 -1.2252731e-002;
                         1.2812565e-001  2.2138052e-002  2.3019662e-002;
                         1.3975507e-002 -4.6779580e-002 -5.1687796e-002]''')


class TestNumpyMatrixFileDataSet(unittest.TestCase):
  __FILE = "../sparse_autoencoder/matlab/src/olsh.dat"
  __LINES = 5120

  def test_len(self):
    lns = self.__LINES
    self.assertEqual(256, len(MatFileDataSet(self.__FILE)))
    self.assertEqual(103, len(MatFileDataSet(self.__FILE, slice_size=50)))
    self.assertEqual(52, len(MatFileDataSet(self.__FILE, slice_size=99)))
    self.assertEqual(5120, len(MatFileDataSet(self.__FILE, slice_size=1)))
    self.assertEqual(2, len(MatFileDataSet(self.__FILE, slice_size=5119)))

  def test_getitem(self):
    ds1 = MatFileDataSet(self.__FILE)
    ds2 = MatFileDataSet(self.__FILE, slice_size=20)
    ds3 = MatFileDataSet(self.__FILE, slice_size=50)
    ds4 = MatFileDataSet(self.__FILE, slice_size=99)
    ds5 = MatFileDataSet(self.__FILE, slice_size=100)

    self.assertTrue((MAT1 == ds1[0].raw_data()[0:6][:,0:3]).all())
    self.assertTrue((MAT1 == ds2[0].raw_data()[0:6][:,0:3]).all())
    self.assertTrue((MAT1 == ds3[0].raw_data()[0:6][:,0:3]).all())
    self.assertTrue((MAT2 == ds2[100].raw_data()[0:6][:,3:6]).all())
    self.assertTrue((MAT2 == ds3[40].raw_data()[0:6][:,3:6]).all())
    self.assertTrue((MAT2 == ds5[20].raw_data()[0:6][:,3:6]).all())
    self.assertTrue((MAT3 == ds4[15].raw_data()[0:6][:,6:9]).all())

  def test_slices(self):
    ds1 = MatFileDataSet(self.__FILE)
    ds2 = MatFileDataSet(self.__FILE, slice_size=20)
    ds3 = MatFileDataSet(self.__FILE, slice_size=50)
    ds4 = MatFileDataSet(self.__FILE, slice_size=99)
    ds5 = MatFileDataSet(self.__FILE, slice_size=100)

    self.assertTrue((MAT1 == ds1.slice(0).raw_data()[0:6][:,0:3]).all())
    self.assertTrue((MAT1 == ds2.slice(0).raw_data()[0:6][:,0:3]).all())
    self.assertTrue((MAT1 == ds3.slice(0).raw_data()[0:6][:,0:3]).all())
    self.assertTrue((MAT2 == ds2.slice(100).raw_data()[0:6][:,3:6]).all())
    self.assertTrue((MAT2 == ds3.slice(40).raw_data()[0:6][:,3:6]).all())
    self.assertTrue((MAT2 == ds5.slice(20).raw_data()[0:6][:,3:6]).all())
    self.assertTrue((MAT3 == ds4.slice(15).raw_data()[0:6][:,6:9]).all())


  def test_hash(self):
#    for slice_size in [30, 399, 1, 5119]:
    for slice_size in [30, 1]:
      ds1 = MatFileDataSet(self.__FILE, slice_size=slice_size)
      ds2 = MatFileDataSet(self.__FILE, slice_size=slice_size)
      self.assertEqual(ds1.hash(), ds2.hash())
      for i in range(0, len(ds1), 100):
        self.assertEqual(ds1.hash(i), ds2.hash(i))
        slice1 = ds1.slice_from_hash(ds1.hash(i)).raw_data()
        slice2 = ds2.slice_from_hash(ds2.hash(i)).raw_data()
        slice12 = ds1.slice_from_hash(ds2.hash(i)).raw_data()
        slice21 = ds2.slice_from_hash(ds1.hash(i)).raw_data()
        self.assertTrue((slice1 == slice2).all())
        self.assertTrue((slice12 == slice21).all())
        self.assertTrue((slice1 == slice21).all())



