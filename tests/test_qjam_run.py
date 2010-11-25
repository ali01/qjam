import unittest
import subprocess


class TestQjamRun(unittest.TestCase):
  def __get_output(self, cmd):
    print cmd
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

  def test_run1(self):
    cmd = ['bin/qjam-run.py', 'examples.multiply_sum',
           'examples.sequences.onetoten', 'examples.sequences.three']
    output = self.__get_output(cmd)
    self.assertEqual(output, '165\n')

  def test_run_numpy_examples(self):
    cmd = ['bin/qjam-run.py', 'examples.numpy_inner_prod',
           'examples.numpy_inner_prod.x', 'examples.numpy_inner_prod.theta']
    output = self.__get_output(cmd)
    self.assertEqual(output, '170\n')
