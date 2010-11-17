import unittest
import numpy
from . import fixture
from qjam import Job, Master, Node

class NumPyBase(object):
    """Test NumPy inner product calculations."""

    def test_inner_product(self):
        def inner_prod(xs, theta):
            import numpy
            print xs
            print theta
            return sum([numpy.dot(numpy.transpose(theta), xi) for xi in xs])
        x = numpy.array([[1,2],[3,4],[5,6],[7,8],[9,10]])
        job = Job(inner_prod, name='inner_prod',
                  dataset=x, params=numpy.array([2,4]))
        result = self.master.run(job)
        self.assertEqual(None, result)

class TestLocalNumPy(NumPyBase, unittest.TestCase):
    def setUp(self):
        self.master = Master(fixture.localhost_nodes)
