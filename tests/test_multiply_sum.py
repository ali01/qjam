import unittest
from . import fixture
from qjam import Job, Master

class TestMultiplySum(unittest.TestCase):
    """Test with map function `lambda x -> theta[0]*x`, where `theta` is some
    coefficient and the input `x` values are numbers. Expects the sum of the
    `x` values times `theta` as output."""
    
    def test_multiply_sum(self):
        master = Master(fixture.localhost_nodes)
        def multiply_sum(xs, theta):
            return sum([theta*x for x in xs])
        job = Job(multiply_sum, name='multiply_sum',
                  dataset=(1,2,3,4,5,6,7), params=3)
        result = master.run(job)
        self.assertEqual(84, result)

