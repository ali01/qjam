import unittest
from subprocess import Popen, PIPE

class TestQjamRun(unittest.TestCase):
    def test_run1(self):
        cmd = ['bin/qjam-run.py', 'examples.multiply_sum.multiply_sum',
               'examples.sequences.onetoten']
        output = Popen(cmd, stdout=PIPE).communicate()[0]
        self.assertEqual(output, "165\n")

