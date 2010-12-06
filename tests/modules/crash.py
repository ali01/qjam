import sys

def mapfunc(params, dataset):
  print >>sys.stderr, 'I am the mapfunc. I am killing the worker.'
  sys.exit(-1)
