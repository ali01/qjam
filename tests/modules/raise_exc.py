# This module raises an exception when running. This is a test module to ensure
# the worker running the callable will not explode if the callable does not act
# properly.
def mapfunc(params, dataset):
  raise ValueError, 'callable exploded'
