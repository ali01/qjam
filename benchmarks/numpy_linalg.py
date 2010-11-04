import numpy

DEFAULT_SIZE = 50

def matrix_multiplication(size=DEFAULT_SIZE, number=None):
    """Performs `AB = C`."""
    A = numpy.arange(size * size).reshape(size, size)
    B = numpy.arange(size * size,0,-1).reshape(size, size)
    for i in xrange(number):
        C = numpy.dot(A,B)
    return

def elementwise_multiplication(size=DEFAULT_SIZE, number=None):
    """Performs element-wise multiplication `A*B = C`."""
    A = numpy.arange(size * size).reshape(size, size)
    B = numpy.arange(size * size,0,-1).reshape(size, size)
    for i in xrange(number):
        C = A * B
    return

def matrix_transpose(size=DEFAULT_SIZE, number=None):
    """Transposes a matrix."""
    A = numpy.arange(size * size).reshape(size, size)
    for i in xrange(number):
        AT = numpy.transpose(A)
    return

def matrix_addition(size=DEFAULT_SIZE, number=None):
    """Adds two matrices."""
    A = numpy.arange(size * size).reshape(size, size)
    B = numpy.arange(size * size,0,-1).reshape(size, size)
    for i in xrange(number):
        C = A + B
    return

def vector_inner_product(size=DEFAULT_SIZE, number=None):
    """Computes a^T b = c."""
    a = numpy.arange(size)
    b = numpy.arange(size,0,-1)
    for i in xrange(number):
        c = numpy.dot(a,b)
    return

