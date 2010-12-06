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
  def __init__(self, slice_size):
    self.__hash_dict = {}  # slice hash -> slice index
    self.__hash_list = []  # [hash_1, hash_2, ..., hash_n]
    self._slice_size = slice_size

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
  def _hash_slices(self):
    '''Sets up the slice number and their hash values.'''
    # we do not have _slice_hashes yet, so cannot use len()
    hashes = [self.hash(i) for i in range(0, len(self))]
    self._hash_list_is(hashes)

  def _hash_list_is(self, hash_list):
    '''Set up the slice hashes from the given list.'''
    self.__hash_list = hash_list
    for i, hash in enumerate(hash_list):
      self.__hash_dict[hash] = i

  # public
  def slice_size(self):
    '''Returns the dataset's slice_size.'''
    return self._slice_size

  def slice_size_is(self, size):
    if self._slice_size != size:
      self._slice_size = size
      if self.__hash_list:
        # slice_size has changed so previous indices are invalid; rehash
        self._hash_slices()

  def raw_data(self):
    '''Returns a pointer to the raw data. WARNING: DO NOT MODIFY!'''
    return self._data

  def slice_data(self, index):
    '''Returns the raw data that corresponds to the slice at index'''
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

  def slice_from_hash(self, hash_value):
    # hash indices lazily if they haven't been hashed before
    if not self.__hash_list:
      self._hash_slices()

    index = self.__hash_dict[hash_value]
    return self.slice(index)

  def slice_data_from_hash(self, hash_value):
    return self.slice_from_hash(hash_value).raw_data()

  def hash_list(self):
    '''returns a list of the hashes of all slices'''
    # hash indices lazily if they haven't been hashed before
    if not self.__hash_list:
      self._hash_slices()

    return self.__hash_list

  def __len__(self):
    '''Returns the number of slices in the dataset.'''
    return math.ceil(float(self.chunks()) / self.slice_size())

  # subclasses may override:

  # subclasses must implement:
  def chunks(self):
    '''Number of chunks into which the internal data can be divided.'''
    raise NotImplementedError

  def slice(self, index):
    '''Returns the slice of data at the given index.'''
    raise NotImplementedError


class ListDataSet(BaseDataSet):
  '''Basic List DataSet.'''
  def __init__(self, _list, slice_size=30, slice_hashes=None):
    '''The given slice_size determines the number of elements in each slice.'''
    BaseDataSet.__init__(self, slice_size)
    self._data = _list
    if slice_hashes is not None:
      self._hash_list_is(slice_hashes)

  def chunks(self):
    return len(self._data)

  def slice(self, index):
    '''Returns the slice of data at the given index.'''
    if index < 0 or index >= len(self):
      raise KeyError('Slice index %i is out of bounds.' % index)
    data = self._data[self.slice_size()*index : self.slice_size()*(index+1)]
    hashes = [self.hash_list()[index]]
    return ListDataSet(data, slice_size=self.slice_size(), slice_hashes=hashes)


class NumpyMatrixDataSet(BaseDataSet):
  '''Basic DataSet wrapping a numpy Matrix.'''
  def __init__(self, matrix, slice_size=5, row_major=True, slice_hashes=None):
    '''Row major is true if the examples are across rows.'''
    BaseDataSet.__init__(self, slice_size)
    # support easy slicing of column-major matrices:
    self._data = matrix if row_major else matrix.transpose()
    if slice_hashes is not None:
      self._hash_list_is(slice_hashes)

  def chunks(self):
    return self._data.shape[0]

  def slice(self, index):
    '''Returns the slice of the matrix at the given index.'''
    if index < 0 or index >= len(self):
      raise KeyError('Slice index %i is out of bounds.' % index)
    data = self._data[self.slice_size()*index:self.slice_size()*(index+1)]
    hashes = [self.hash_list()[index]]
    return NumpyMatrixDataSet(data, slice_size=self.slice_size(),
                              slice_hashes=hashes)


class NumpyMatrixFileDataSet(BaseDataSet):
  '''Basic DataSet that reads a matrix from a file.'''
  def __init__(self, filename, slice_size=20, row_major=True,
               slice_hashes=None):
    '''Row major is true if the examples are across rows.'''
    BaseDataSet.__init__(self, slice_size)
    # support easy slicing of column-major matrices:
    self._data = filename
    self.filesize() # attempt to get the filesize.
    if slice_hashes is not None:
      self._hash_list_is(slice_hashes)

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

  def chunks(self):
    return self.line_count()

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
    hashes = [self.hash_list()[index]]
    return NumpyMatrixDataSet(matrix, slice_size=self.slice_size(),
                              slice_hashes=hashes)

