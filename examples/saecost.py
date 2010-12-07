import random
import numpy as np
from scipy import optimize as opt
import time
import math
import sys

def saecost (WB, dataset):
    
    func_count = 0;
    lambda_W = 0.002
    lambda_p = 4
    numL1units = 64;
    numL2units = 30;
    numL3units = 64;
    
    rho = 0.002
    
    inputSize = dataset.shape[1];
    numExamples = dataset.shape[0];
    outputSize = inputSize;

    # Vector to Layers
    W1 = WB[0 : numL1units*numL2units].reshape (numL2units, numL1units, order='C')
    W2 = WB[numL1units*numL2units : numL1units*numL2units + numL2units*numL3units].reshape (numL3units, numL2units, order='C')
    B1 = WB[numL1units*numL2units + numL2units*numL3units : numL1units*numL2units + numL2units*numL3units + numL2units]
    B2 = WB[numL1units*numL2units + numL2units*numL3units + numL2units : numL1units*numL2units + numL2units*numL3units + numL2units + numL3units]

    b1 = np.tile(B1.reshape(numL2units,1), numExamples); #repmat(b1, 1, numExamples);
    b2 = np.tile(B2.reshape(numL3units,1), numExamples); #repmat(b2, 1, numExamples);

    a1 = np.transpose(dataset);

    z2 = np.dot(W1,a1) + b1; #W1 * a1 + b1;
    a2 = np.tanh(z2);

    z3 = np.dot(W2,a2) + b2; #W2 * a2 + b2;
    a3 = np.tanh(z3);

    p2 = np.sum(.5 * (1 + a2), 1) / numExamples

    cost = (.5 / numExamples) * np.sum((a1 - a3)**2) \
       + .5 * lambda_W *(np.sum(W1**2) + np.sum(W2**2)) \
       + lambda_p * np.sum(rho * np.log(rho / p2) + (1 - rho) * np.log((1 - rho) / (1 - p2)));

    delta3 = -np.multiply((a1 - a3) , (1 - a3**2));
    delta2 = np.multiply(np.dot(np.transpose(W2), delta3), (1 - a2**2));

    deltap = (.5 / numExamples) * (1 - a2**2);
    deltakL = (1 - rho) / (1 - p2) - (rho / p2);
    deltakL = np.multiply(np.tile(np.reshape(deltakL, (numL2units,1)), numExamples), deltap);

    gradW1 = (1.0 / numExamples) * np.dot(delta2, np.transpose(a1)) \
       + lambda_W * W1 \
       + lambda_p * np.dot(deltakL, np.transpose(a1))

    gradb1 = (1.0 / numExamples) * np.dot(delta2, np.ones((numExamples, 1))) \
       + lambda_p * np.dot(deltakL, np.ones((numExamples, 1)))

    gradW2 = (1.0 / numExamples) * np.dot(delta3, np.transpose(a2)) \
       + lambda_W * W2;

    gradb2 = (1.0 / numExamples) * np.dot(delta3, np.ones((numExamples, 1)));

    grad = np.concatenate((gradW1.reshape(numL2units*numL1units,), gradW2.reshape(numL2units*numL3units,), gradb1.reshape(numL2units,), gradb2.reshape(numL3units,)))
    return cost, grad;
# End SAECostFunction

mapfunc = saecost
