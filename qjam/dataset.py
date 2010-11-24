'''DataSet objects wrap underlying data, with an accessor for a particular of
data (termed slice).'''

import os
import numpy
import math
import hashlib
import cPickle as pickle

def hash_objects(*args):
  '''Hash function of to use with the DataSets. Use sha1 by default.'''
  hashobj = hashlib.sha1()
  for arg in args:
    hashobj.update(str(arg))
  return hashobj.hexdigest()

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
      if key < 0 or key >= len(self):
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

  # protected
  def _hash_slice_indices(self, slice_size):
    '''Sets up the slice number and their hash values.'''
    # we do not have _slice_hashes yet, so cannot use len()
    self._slice_size = slice_size
    self._slice_hashes = {}
    for i in range(0, len(self)):
      self._slice_hashes[self.hash(i)] = i

  # public
  def slice_size(self):
    '''Returns the dataset's slice_size.'''
    return self._slice_size

  def raw_data(self):
    '''Returns a pointer to the raw data. WARNING: DO NOT MODIFY!'''
    return self._data

  def slice_data(self, index):
    if index < 0 or index >= len(self):
      raise KeyError('Slice index %i is out of bounds.' % index)
    return self.slice(index).raw_data()

  def hash(self, index=None):
    '''Returns the hash of the slice of data at the given index.
    If index not given, return the hash that uniquely identifies this data set.
    '''
    if index:
      if index < 0 or index >= len(self):
        raise KeyError('Slice index %i is out of bounds.' % index)

      return hash_objects(self.hash(), index)

    if not hasattr(self, '_hash'):
      self._hash = hash_objects(pickle.dumps(self))
    return self._hash

  def slice_with_hash(self, hash_value):
    index = self._slice_hashes[hash_value]
    return self.slice(index)

  # subclasses may override:

  # subclasses must implement:
  def __len__(self):
    '''Returns the length of data.'''
    raise NotImplementedError

  def slice(self, index):
    '''Returns the slice of data at the given index.'''
    raise NotImplementedError


class ListDataSet(BaseDataSet):
  '''Basic List DataSet.'''
  def __init__(self, _list, slice_size=30):
    '''The given slice_size determines the number of elements in each slice.'''
    self._data = _list
    self._hash_slice_indices(slice_size)

  def __len__(self):
    '''Returns the length of data list.'''
    return math.ceil(len(self._data) * 1.0 / self.slice_size())

  def slice(self, index):
    '''Returns the slice of data at the given index.'''
    if index < 0 or index >= len(self):
      raise KeyError('Slice index %i is out of bounds.' % index)
    data = self._data[self.slice_size()*index : self.slice_size()*(index+1)]
    return ListDataSet(data, slice_size=self.slice_size())


class NumpyMatrixDataSet(BaseDataSet):
  '''Basic DataSet wrapping a numpy Matrix.'''
  def __init__(self, matrix, slice_size=5, row_major=True):
    '''Row major is true if the examples are across rows.'''
    # support easy slicing of column-major matrices:
    self._data = matrix if row_major else matrix.transpose()
    self._hash_slice_indices(slice_size)

  def __len__(self):
    '''Returns the number of entries (major) in the matrix.'''
    return math.ceil(self._data.shape[0] * 1.0 / self.slice_size())

  def slice(self, index):
    '''Returns the slice of the matrix at the given index.'''
    if index < 0 or index >= len(self):
      raise KeyError('Slice index %i is out of bounds.' % index)
    data = self._data[self.slice_size()*index:self.slice_size()*(index+1)]
    return NumpyMatrixDataSet(data, slice_size=self.slice_size())


class NumpyMatrixFileDataSet(BaseDataSet):
  '''Basic DataSet that reads a matrix from a file.'''
  def __init__(self, filename, slice_size=20, row_major=True):
    '''Row major is true if the examples are across rows.'''
    # support easy slicing of column-major matrices:
    self._data = filename
    self.filesize() # attempt to get the filesize.
    self._hash_slice_indices(slice_size)

  def line_count(self):
    '''Returns the line count of the file.'''
    if not hasattr(self, '_line_count'):
      with open(self._data) as f:
        for i, l in enumerate(f):
          pass
      self._line_count = i + 1
    return self._line_count

  def filesize(self):
    '''Returns the size of the file in bytes.'''
    # attempt to read in the filesize:
    if not hasattr(self, '_filesize') or not self._filesize:
      if os.path.exists(self._data) and os.path.isfile(self._data):
        self._filesize = os.path.getsize(self._data)

    return self._filesize if hasattr(self, '_filesize') else None

  def __len__(self):
    '''Returns the number of entries (major) in the matrix.'''
    return math.ceil(self.line_count() * 1.0 / self.slice_size())

  def slice(self, index):
    if index < 0 or index >= len(self):
      raise KeyError('Slice index %i is out of bounds.' % index)
    '''Returns the slice of the matrix at the given index.'''
    bytes_per_line = int(self.filesize() * 1.0 / self.line_count())
    if int(bytes_per_line) != bytes_per_line:
      raise 'DataSet file not aligned. Lines MUST be of the same length.'

    bytes_per_slice = self.slice_size() * bytes_per_line
    byte_offset = index * bytes_per_slice

    # i'm not proud of this following code, but it seems a reasnoably efficient
    # way to do it. (rather than creating a bunch of big mat objects via concat)
    string = '['
    lines_to_read = self.slice_size()
    with open(self._data, 'r') as f:
      f.seek(byte_offset)
      for line in f:
        string += line.strip() + ';'
        lines_to_read -= 1
        if lines_to_read <= 0:
          break
    string = string.strip(';')
    string += ']'

    matrix = numpy.mat(string.strip())
    return NumpyMatrixDataSet(matrix, slice_size=self.slice_size())

