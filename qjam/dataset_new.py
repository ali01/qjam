'''DataSet objects wrap underlying data, with an accessor for a particular of data (termed slice).'''

import numpy
import math

def DataSet(raw_data, **kwds):
  if isinstance(raw_data, BaseDataSet):
    return raw_data
  elif isinstance(raw_data, list) or isinstance(raw_data, tuple):
    return ListDataSet(raw_data, **kwds)
  elif isinstance(raw_data, numpy.ndarray):
    return NumpyMatrixDataSet(raw_data, **kwds)

class BaseDataSet(object):
  def __getitem__(self, key):
    '''Accessor for the slice of data at the given key (index or seq slice).'''
    if isinstance(key, int):
      if key > len(self):
        raise KeyError('Slice index %i is out of bounds.' % key)
      return self.slice(key)

    if isinstance(key, slice):
      start = key.start if key.start else 0
      stop = key.stop if key.stop else len(self.slices(index)) - key.start
      step = key.step if key.step else 1
      slices = list()
      for index in range(start, stop, step):
        slices.append(self.slice(index))
      return slices

    raise TypeError('Slice index is not an integer or a slice.')

  # subclasses must implement:
  def __len__(self):
    '''Returns the length of data.'''
    raise NotImplementedError

  def slice(index):
    '''Returns the slice of data at the given index.'''
    raise NotImplementedError


class ListDataSet(BaseDataSet):
  def __init__(self, _list, slice_size=30):
    '''The given slice_size determines the number of elements in each slice.'''
    self.__list = _list
    self.__slice_size = int(slice_size)

  def __len__(self):
    '''Returns the length of data list.'''
    return math.ceil(len(self.__list) * 1.0 / self.__slice_size)

  def slice(self, index):
    '''Returns the slice of data at the given index.'''
    return self.__list[self.__slice_size*index : self.__slice_size*(index+1)]


class NumpyMatrixDataSet(BaseDataSet):
  def __init__(self, matrix, slice_size=5, row_major=True):
    '''Row major is true if the examples are across rows.'''
    self.__slice_size = int(slice_size)
    self.__matrix = matrix if row_major else matrix.transpose()
    # this is to supposrt easy slicing of column-major matrices. ^
    # however, this could be bad if we're just copying around large matrices...

  def __len__(self):
    '''Returns the number of entries (major) in the matrix.'''
    return math.ceil(self.__matrix.shape[0] * 1.0 / self.__slice_size)

  def slice(self, index):
    '''Returns the slice of the matrix at the given index.'''
    return self.__matrix[self.__slice_size*index:self.__slice_size*(index+1)]


