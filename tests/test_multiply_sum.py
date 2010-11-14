import unittest
from . import fixture
from qjam import Job, Master

class TestMultiplySum(unittest.TestCase):
    """Test with map function `lambda x -> theta*x`, where `theta` is some
    coefficient and the input `x` values are numbers. Expects the sum of the
    `x` values times `theta` as output."""

    def setUp(self):
        self.master = Master(fixture.localhost_nodes)
        
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
            time.sleep(0.6)
            return sum([theta*x for x in xs])
        job = Job(slow_multiply_sum, name='slow_multiply_sum',
                  dataset=(1,2,3,4,5,6,7), params=3)
        result = self.master.run(job)
        self.assertEqual(84, result)
        

