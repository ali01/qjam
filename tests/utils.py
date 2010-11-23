#!/usr/bin/python
import base64
import cPickle as pickle


def source(module):
  '''Return the source code for a given module object.'''
  filename = module.__file__
  filename = filename.replace('.pyc', '.py')
  with open(filename, 'r') as fh:
    return fh.read()


def encode(data):
  return base64.b64encode(pickle.dumps(data))


def decode(data):
  return pickle.loads(base64.b64decode(data))
