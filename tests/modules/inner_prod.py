import numpy

def mapfunc(params, dataset):
  return sum([numpy.dot(numpy.transpose(params), x) for x in dataset])
