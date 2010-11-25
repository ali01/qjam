import numpy


def sum_dataset(params, dataset):
  '''Returns the sum of all of the elements in the dataset. The dataset is
  assumed to be a numpy object (an array or matrix).'''
  return numpy.sum(dataset)


mapfunc = sum_dataset
