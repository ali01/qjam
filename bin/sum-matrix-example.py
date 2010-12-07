#!/usr/bin/env python2.6
'''
This is a very simple program to illustrate how to use the qjam framework. It
shows how to:

  * create a pool of workers
  * create a simple DataSet object out of a numpy matrix
  * start a qjam master
  * run a job on the worker pool and retrieve the result

All of the significant pieces are sufficiently commented to help you understand
how to write programs to use qjam.
'''
import logging
import os
import sys

import numpy

# Set up import path to qjam.
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))

from qjam.dataset import NumpyMatrixDataSet
from qjam.master.master import Master
from qjam.master.remote_worker import RemoteWorker

# sum_dataset is an example module that contains a function that is run on each
# piece of the dataset.
from examples import sum_dataset


def main():
  _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  logging.basicConfig(level=logging.INFO, format=_fmt)

  # Worker hostnames are the commandline options. Each hostname specified on
  # the commandline will be bootstrapped and have a worker started on it.
  if len(sys.argv) < 2:
    print 'usage: %s <matrixsize> [<worker> ...]' % sys.argv[0]
    sys.exit(1)
  matsize = int(sys.argv[1])
  hostnames = sys.argv[2:] or ['localhost']

  # Start the worker processes on the specified hostnames.
  workers = []
  for i, hostname in enumerate(hostnames):
    worker = RemoteWorker(hostname)
    workers.append(worker)
    print 'Started worker %d on %s' % (i, hostname)
  print

  # Create a numpy matrix.
  X = numpy.random.permutation(numpy.arange(1,matsize*matsize+1))
  X = X.reshape(matsize, matsize)

  print 'Creating and permuting %dx%d matrix X with integers 1 .. %d^2' % \
      (matsize, matsize, matsize)
  numpy.set_printoptions(threshold=256)
  print 'X = %s' % (str(X).replace("\n", "\n    "))
  exp_sum = (1+matsize**2)*(matsize**2)/2
  print 'Expected element sum of X = %d = (1/2)(%d^2+1)(%d^2)' % \
      (exp_sum, matsize, matsize)

  # Create a DataSet object from this matrix.
  #
  # DataSet objects are necessary so the framework can determine how to split
  # up the data into smaller chunks and distribute the chunks to the workers.
  dataset = NumpyMatrixDataSet(X)

  # Sum the matrix!
  master = Master(workers)
  params = None  # No parameters needed for this job.
  result = master.run(sum_dataset, params, dataset)

  # Print the result.
  print 'Computed element sum of X = %d' % result


if __name__ == '__main__':
  main()
