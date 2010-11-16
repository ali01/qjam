import unittest
from . import fixture
from qjam import Job, Master, Node

class MultiplySumBase(object):
    """Test with map function `lambda x -> theta*x`, where `theta` is some
    coefficient and the input `x` values are numbers. Expects the sum of the
    `x` values times `theta` as output."""

    def test_multiply_sum(self):
        def multiply_sum(xs, theta):
            return sum([theta*x for x in xs])
        job = Job(multiply_sum, name='multiply_sum',
                  dataset=(1,2,3,4,5,6,7), params=3)
        result = self.master.run(job)
        self.assertEqual(84, result)

    def test_slow_multiply_sum(self):
        def slow_multiply_sum(xs, theta):
            import time
            time.sleep(0.2)
            return sum([theta*x for x in xs])
        job = Job(slow_multiply_sum, name='slow_multiply_sum',
                  dataset=(1,2,3,4,5,6,7), params=3)
        result = self.master.run(job)
        self.assertEqual(84, result)

    def test_differential_sleep_multiply_sum(self):
        def differential_sleep_multiply_sum(xs, theta):
            import time
            time.sleep(0.05 * xs[0])
            return sum([theta*x for x in xs])
        job = Job(differential_sleep_multiply_sum,
                  name='differential_sleep_multiply_sum',
                  dataset=(1,2,3,4,5,6,7), params=3)
        result = self.master.run(job)
        self.assertEqual(84, result)
        
class TestLocalMultiplySum(MultiplySumBase, unittest.TestCase):
    def setUp(self):
        self.master = Master(fixture.localhost_nodes)
        
class TestRemoteMultiplySum(MultiplySumBase, unittest.TestCase):
    def setUp(self):
        self.master = Master([Node('127.0.0.1')])
        
class TestClusterMultiplySum(MultiplySumBase, unittest.TestCase):
    def setUp(self):
        self.master = Master([Node('127.0.0.1', 2000),
                              Node('127.0.0.1', 2001),
                              Node('127.0.0.1', 2002)])
