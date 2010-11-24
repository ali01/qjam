import numpy

def run(params, dataset):
  return sum([numpy.dot(numpy.transpose(params), x) for x in dataset])
