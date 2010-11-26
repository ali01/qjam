#import sys # remove interpreter and add it again
import random
import numpy
from scipy import optimize as opt
import time
import math

numpy.seterr(over='raise') # Raise error in case of overflow

def sparse_autoencoder_costfunc(WB, master, mod, params, X):
    p = params
    lambda_W = p['lambda_W']
    lambda_p = p['lambda_p']
    rho = p['rho']
    numL1units = p['numL1units']
    numL2units = p['numL2units']
    numL3units = p['numL3units']

    inputSize = X.raw_data().shape[1]
    numExamples = X.raw_data().shape[0]
    outputSize = inputSize

    # Vector to Layers
    W1 = WB[0 : p['numL1units']*p['numL2units']].reshape(p['numL2units'], p['numL1units'], order='C')
    W2 = WB[p['numL1units']*p['numL2units'] : p['numL1units']*p['numL2units'] + p['numL2units']*p['numL3units']].reshape(p['numL3units'], p['numL2units'], order='C')
    B1 = WB[p['numL1units']*p['numL2units'] + p['numL2units']*p['numL3units'] : p['numL1units']*p['numL2units'] + p['numL2units']*p['numL3units'] + p['numL2units']]
    B2 = WB[p['numL1units']*p['numL2units'] + p['numL2units']*p['numL3units'] + p['numL2units'] : p['numL1units']*p['numL2units'] + p['numL2units']*p['numL3units'] + p['numL2units'] + p['numL3units']]

    b1 = numpy.tile(B1.reshape(p['numL2units'],1), numExamples); #repmat(b1, 1, numExamples);
    b2 = numpy.tile(B2.reshape(p['numL3units'],1), numExamples); #repmat(b2, 1, numExamples);

    a1 = numpy.transpose(X.raw_data())

    z2 = numpy.dot(W1,a1) + b1 #W1 * a1 + b1;
    a2 = numpy.tanh(z2)

    z3 = numpy.dot(W2,a2) + b2 #W2 * a2 + b2;
    a3 = numpy.tanh(z3)

    p2 = numpy.sum(.5 * (1 + a2), 1) / numExamples

    cost = (.5 / numExamples) * numpy.sum((a1 - a3)**2) \
       + .5 * lambda_W *(numpy.sum(W1**2) + numpy.sum(W2**2)) \
       + lambda_p * numpy.sum(rho * numpy.log(rho / p2) + (1 - rho) * numpy.log((1 - rho) / (1 - p2)));

    delta3 = -numpy.multiply((a1 - a3) , (1 - a3**2));
    delta2 = numpy.multiply(numpy.dot(numpy.transpose(W2), delta3), (1 - a2**2));

    deltap = (.5 / numExamples) * (1 - a2**2);
    deltakL = (1 - rho) / (1 - p2) - (rho / p2);
    deltakL = numpy.multiply(numpy.tile(numpy.reshape(deltakL, (numL2units,1)), numExamples), deltap);

    gradW1 = (1.0 / numExamples) * numpy.dot(delta2, numpy.transpose(a1)) \
       + lambda_W * W1 \
       + lambda_p * numpy.dot(deltakL, numpy.transpose(a1))

    gradb1 = (1.0 / numExamples) * numpy.dot(delta2, numpy.ones((numExamples, 1))) \
       + lambda_p * numpy.dot(deltakL, numpy.ones((numExamples, 1)))

    gradW2 = (1.0 / numExamples) * numpy.dot(delta3, numpy.transpose(a2)) \
       + lambda_W * W2;

    gradb2 = (1.0 / numExamples) * numpy.dot(delta3, numpy.ones((numExamples, 1)));

    grad = numpy.concatenate((gradW1.reshape(numL2units*numL1units,), gradW2.reshape(numL2units*numL3units,), gradb1.reshape(numL2units,), gradb2.reshape(numL3units,)))

    return cost, grad;
# End SAECostFunction

def make_initial_args(olsh_path):
    # Initialize constants
    p = dict(
        imgSize=512,
        numImages=10,
        lambda_W=0.002,
        lambda_p=4,
        patchSize=8,
        numL1units=64,
        numL2units=30,
        numL3units=64,
        numPatches=numpy.power(10, 5),

        beta=5, # not used in optimize package
        rho=0.002, # add sparsity term later !!!
        alpha=0.003, # not used in optimize package
    )

    # Read in images - make global vars
    allImages = numpy.loadtxt(olsh_path)
    # Make sure that these are ordered the right way when reshaping???
    images = allImages.reshape(p['numImages'], p['imgSize'], p['imgSize']) # i.e. (10, 512, 512)

    # Initialize parameters
    q1 = 64
    W1 = numpy.random.rand(p['numL2units'], p['numL1units']) * (1 / numpy.sqrt(q1))

    q2 = 30
    W2 = numpy.random.rand(p['numL3units'], p['numL2units']) * (1 / numpy.sqrt(q2))

    # Initialize bias units
    b1 = numpy.zeros((p['numL2units'], 1))
    b2 = numpy.zeros((p['numL3units'], 1))

    WB0 = numpy.concatenate((W1.reshape(p['numL2units']*p['numL1units'],1), W2.reshape(p['numL2units']*p['numL3units'],1), b1, b2))
    WB0 = numpy.asfortranarray(WB0)

    # Generate input and output i.e X and Y
    # Each row is a patch.
    X = numpy.zeros((p['numPatches'], p['patchSize']*p['patchSize']))
    for iter in range(0,p['numPatches']):
        # Create an training example, 8x8 patch from image
        randImageNum = random.randint(0,p['numImages']-1) # randomly pick one of the 10 images
        randRow = random.randint(0, p['imgSize'] - p['patchSize']) # randomly pick a starting row for patch
        randCol = random.randint(0, p['imgSize'] - p['patchSize']) # randomly pick a starting col for patch
        patch = images[randImageNum, randRow:randRow + p['patchSize'], randCol:randCol + p['patchSize']]
        patch = patch.reshape((p['patchSize']*p['patchSize']), 1, order='F') # reshape as a 64x1 vector to be used as input
        X[iter,:] = patch.T

    return p, X, WB0


# Main starts here
if __name__ == '__main__':
    import sys
    from qjam.dataset import NumpyMatrixDataSet
    from qjam.master import Master, RemoteWorker

    if len(sys.argv) == 1:
        print "sparse autoencoder\nusage: %s <olsh.dat> [<hostname> ...]" % sys.argv[0]
        exit(1)
    olsh_path = sys.argv[1]
    cluster = sys.argv[2:]
    if not cluster:
        cluster = ['localhost']

    master = Master([RemoteWorker(host) for host in cluster])
    params, X, WB0 = make_initial_args(olsh_path)
    X = NumpyMatrixDataSet(X)
    mod = sys.modules[__name__]

    result_list = opt.fmin_l_bfgs_b(
        sparse_autoencoder_costfunc,
        WB0, fprime=None,
        args=(master, mod, params, X), approx_grad=0, bounds=None,
        m=10, factr=1e12, maxfun=500,
        pgtol=1.0000000000000001e-04, epsilon=0.001, iprint=1,
    )

    opt_params = result_list

    print 'optimal W = ', opt_params[0]
    print 'minimum SAECostFunction = ', opt_params[1]
    print 'output information =', opt_params[2]

    W1 = opt_params[0][0 : numL1units*numL2units].reshape(numL2units, numL1units, order='C')

    # Write run parameters to file
    # Note the best way to do this but works and data is small
    outputFileHandle = open("LBFGS_w1.dat", 'w')
    for i in range(0, W1.shape[0]):
        for j in range(0, W1.shape[1]):
            outputFileHandle.write(str(W1[i,j])+ ' ')
        outputFileHandle.write('\n')
    outputFileHandle.close()

