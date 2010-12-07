#import sys # remove interpreter and add it again
import random
import numpy as np
from scipy import optimize as opt
import time
import math
import sys
import saecost
import logging
import os
import sys

global imgSize
global numImages
global filename
global lambdap
global numL1units
global numL2units
global numL3units
global X
global rho
global cg_iter
global lambda_p
global func_count
global master
global dataset

def sae_test ():
    time.clock()
    np.seterr(over='raise') # Raise error in case of overflow

    from qjam.master.master import Master
    from qjam.master.remote_worker import RemoteWorker
    from qjam.dataset import NumpyMatrixDataSet

    cluster = sys.argv[2:]
    if not cluster:
        cluster = ['localhost']

    global master
    master = Master([RemoteWorker(host) for host in cluster])

    global imgSize
    global numImages
    global filename
    global lambdap
    global numL1units
    global numL2units
    global numL3units
    global X
    global rho
    global cg_iter
    global lambda_W
    global lambda_p
    global func_count
    global dataset

    # Initialize constants
    imgSize = 512;
    numImages = 10;
    filename = 'olsh.dat';
    lambda_W = 0.002
    lambda_p = 4
    patchSize = 8;
    numL1units = 64;
    numL2units = 30;
    numL3units = 64;
    numPatches = int(sys.argv[1])

    beta = 5 # not used in optimize package
    rho = 0.002 # add sparsity term later !!!
    alpha = 0.003 # not used in optimize package

    # Read in images - make global vars
    allImages = np.loadtxt(filename);
    # Make sure that these are ordered the right way when reshaping???
    images = allImages.reshape(numImages, imgSize, imgSize) # i.e. (10, 512, 512)

    # Initialize parameters
    q1 = 64;
    W1 = np.random.rand(numL2units, numL1units) * (1 / np.sqrt(q1));

    q2 = 30;
    W2 = np.random.rand(numL3units, numL2units) * (1 / np.sqrt(q2));

    # Initialize bias units
    b1 = np.zeros((numL2units, 1))
    b2 = np.zeros((numL3units, 1))

    WB0 = np.concatenate((W1.reshape(numL2units*numL1units,1), W2.reshape(numL2units*numL3units,1), b1, b2));
    WB0 = np.asfortranarray(WB0);

    # Generate input and output i.e X and Y
    # Each row is a patch.
    X = np.zeros((numPatches, patchSize*patchSize))
    for iter in range(0,numPatches):
        # Create an training example, 8x8 patch fro2m image
        randImageNum = random.randint(0,numImages-1); # randomly pick one of the 10 images
        randRow = random.randint(0, imgSize - patchSize); # randomly pick a starting row for patch
        randCol = random.randint(0, imgSize - patchSize); # randomly pick a starting col for patch
        patch = images[randImageNum, randRow:randRow + patchSize, randCol:randCol + patchSize];
        patch = patch.reshape((patchSize*patchSize), 1, order='F') # reshape as a 64x1 vector to be used as input
        X[iter,:] = patch.T

    dataset = NumpyMatrixDataSet(X)

    func_count = 0;
    result_list = opt.fmin_l_bfgs_b(parallelSAECostFunction, WB0, fprime = None, \
       args = (), approx_grad = 0, bounds = None, m = 10, factr = 1e4, \
       pgtol = 1.0000000000000001e-04 , epsilon = 0.001, iprint = 1,
       maxfun = 500);

    print 'Run time: ', time.clock() / 60

    opt_params = result_list

    print 'optimal W = ', opt_params[0];
    print 'minimum SAECostFunction = ', opt_params[1];
    print 'output information =', opt_params[2];

    W1 = opt_params[0][0 : numL1units*numL2units].reshape (numL2units, numL1units, order='C')

    # Write run parameters to file
    # Note the best way to do this but works and data is small
    outputFileHandle = open("LBFGS_w1.dat", 'w')
    for i in range(0, W1.shape[0]):
        for j in range(0, W1.shape[1]):
            outputFileHandle.write(str(W1[i,j])+ ' ')
        outputFileHandle.write('\n')
    outputFileHandle.close()
# End sparse_autoencoder

def parallelSAECostFunction(WB) :
    result = master.run(saecost, WB, dataset)
    return result

# Main starts here
if __name__ == '__main__':
    _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=_fmt)

    # Raise error in case of an overflow
    np.seterr(over='raise');

    sae_test(); # normal run
    #cProfile.run('sae_test()', 'sae_prof.bin') # profiler run, save as binary so that it can be reloaded and used with the stats packages

# End main



