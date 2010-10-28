#!/usr/bin/env python
'''
Implementation of the Sparse Autoencoder algorithm.
  (based on Ali's matlab implementation)

@author Juan Batiz-Benet <jbenet@cs.stanford.edu>

Note:
  I found this matlab to numpy ref extremely helpful:
  http://mathesaurus.sourceforge.net/matlab-numpy.html
'''

import sys
from numpy import matlib
from numpy.matlib import multiply
from numpy.matlib import power

import trainingset
SIZE_IMG = 512
SIZE_IMG_SAMPLE = 8


def printProgress(progress):
  if progress == 1:
    print '\rDone!               '
  else:
    print '\rProgress: %02.02f%%' % (float(progress) * 100.0),
  sys.stdout.flush()


class SparseAutoencoder(object):
  '''Implements the Sparse Autoencoder algorithm.'''

  # Autoencoder parameters
  LR_BT = 5

  RHO = -0.996
  ALPHA = 0.007
  LAMBDA = 0.002
  ITERATIONS = 1e3

  FEATURES = 64
  HIDDEN = 30

  def __init__(self, trainingSet):
    self.trainingSet_ = trainingSet

    # initialize weights
    self.weights1_ = matlib.rand(self.HIDDEN, self.FEATURES)
    self.weights1_ /= matlib.sqrt(self.FEATURES)

    self.weights2_ = matlib.rand(self.FEATURES, self.HIDDEN)
    self.weights2_ /= matlib.sqrt(self.HIDDEN)

    # initialize bias
    self.bias1_ = matlib.zeros((self.HIDDEN, ))
    self.bias2_ = matlib.zeros((self.FEATURES, ))

    # initialize rho estimate vector
    self.rho_est_ = matlib.zeros((self.HIDDEN, )).T


  def images(self):
    '''Returns the collection of images.'''
    return self.images_

  def trainingExample(self):
    '''Returns a subsequent training example.'''
    sample = self.trainingSet_.get_example(SIZE_IMG_SAMPLE, SIZE_IMG_SAMPLE)
    return matlib.matrix(sample).T

  def run(self, iterations):
    printProgress(0.0)
    for i in xrange(0, iterations):
      if i % 10000 == 0:
        printProgress(float(i) / iterations)
      self.iteration_()
    printProgress(1)

  def outputWeights(self):
    '''Returns the learned output weights matrix.'''
    return self.weights1_;

  def iteration_(self):
    '''Runs one iteration of the Sparse Autoencoder Algorithm.'''
    self.feedForward_()
    self.backPropagate_()
    self.gradientDescent_()
    self.rhoUpdate_()

  def feedForward_(self):
    '''FeedForward pass (computing activations).'''
    self.x__ = self.trainingExample()

    # hidden layer
    self.z2__ = self.weights1_ * self.x__ + self.bias1_.T
    self.a2__ = matlib.tanh(self.z2__)

    # output layer
    self.z3__ = self.weights2_ * self.a2__ + self.bias2_.T
    self.a3__ = matlib.tanh(self.z3__)

  def backPropagate_(self):
    '''Back-Propagate errors (and node responsibilities).'''
    self.d3__ = multiply(-(self.x__ - self.a3__), 1 - power(self.a3__, 2))
    self.d2__ = multiply(self.weights2_.T * self.d3__, 1 - power(self.a2__, 2))

  def gradientDescent_(self):
    '''Gradient Descent (updating parameters).'''
    self.weights1_ -= (self.ALPHA *
      (self.d2__ * self.x__.T + self.LAMBDA * self.weights1_))
    self.bias1_ -= self.ALPHA * self.d2__.T

    self.weights2_ -= (self.ALPHA *
      (self.d3__ * self.a2__.T + self.LAMBDA * self.weights2_))
    self.bias2_ -= self.ALPHA * self.d3__.T

  def rhoUpdate_(self):
    '''Updating running rho estimate vector.'''
    self.rho_est_ = 0.999 * self.rho_est_ + 0.001 * self.a2__

    # updating hidden layer intercept terms based on rho estimate vector
    self.bias1_ -= self.ALPHA * self.LR_BT * (self.rho_est_.T - self.RHO)


def main():
  if len(sys.argv) == 4:
    imagesFile = sys.argv[1]
    outputFile = sys.argv[2]
    iterations = int(sys.argv[3])

    print 'Running sparse autoencoder with %d iterations' % iterations
    print 'Training set file:', imagesFile
    print 'Output file:', outputFile

    try:
      ts = trainingset.ImageTrainingSet(imagesFile)
    except Exception, e:
      print 'Error loading training set: %s' % e
      return

    sa = SparseAutoencoder(ts)
    sa.run(iterations)
    with open(outputFile, 'w') as f:
      for row in xrange(0, sa.outputWeights().shape[0]):
        for col in xrange(0, sa.outputWeights().shape[1]):
          f.write('%f ' % sa.outputWeights()[row, col])
        f.write('\n')

  else:
    print 'Usage: ', sys.argv[0],
    print '<training set file> <output file> <iterations>'

if __name__ == '__main__':
  main()
