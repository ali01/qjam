from nose.tools import *

from qjam.common import reducing


class Test_Reducing:
  def test_sum_ints(self):
    '''Sum two ints.'''
    result1 = 42
    result2 = 34
    result = reducing.default_reduce(result1, result2)
    assert_equals(result1 + result2, result)

  def test_sum_floats(self):
    '''Sum two floats.'''
    result1 = 42.0
    result2 = 34.0
    result = reducing.default_reduce(result1, result2)
    assert_equals(result1 + result2, result)

  def test_sum_int_float(self):
    '''Sum an int and a float.'''
    result1 = 42.0
    result2 = 34.0
    result = reducing.default_reduce(result1, result2)
    assert_equals(result1 + result2, result)

  def test_sum_int_str(self):
    '''Sum an int and a string.'''
    result1 = 42
    result2 = 'foobar'
    assert_raises(TypeError, reducing.default_reduce, result1, result2)

  def test_sum_lists(self):
    '''Sum two lists of numbers.'''
    result1 = [1, 2, 3]
    result2 = [4, 6, 7]
    combined = [5, 8, 10]
    result = reducing.default_reduce(result1, result2)
    assert_equals(combined, result)

  def test_sum_lists_bad_length(self):
    '''Sum two lists of different lengths.'''
    result1 = [1, 2, 3]
    result2 = [4, 6]
    assert_raises(TypeError, reducing.default_reduce, result1, result2)

  def test_sum_tuple_and_list(self):
    '''Sum a tuple and a list.'''
    result1 = (1, 2, 3)
    result2 = [4, 6, 7]
    combined = [5, 8, 10]
    result = reducing.default_reduce(result1, result2)
    assert_equals(combined, result)
