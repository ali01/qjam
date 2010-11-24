import numpy

def inner_prod(theta, xs):
    import numpy
    return sum([numpy.dot(numpy.transpose(theta), xi) for xi in xs])

x = numpy.array([[1,2],[3,4],[5,6],[7,8],[9,10]])
theta = numpy.array([2,4])
mapfunc = inner_prod
