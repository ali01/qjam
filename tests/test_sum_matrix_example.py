from nose.tools import *
import subprocess


class TestSumMatrixExample:
  def __get_output(self, cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

  def run_with_hosts(self, hosts):
    cmd = ['bin/sum-matrix-example.py']
    cmd.extend(hosts)
    output = self.__get_output(cmd)
    assert_true('Result is: 78\n' in output)

  def test_run1(self):
    self.run_with_hosts(['localhost'])

  def test_run2(self):
    self.run_with_hosts(['localhost', 'localhost'])

  def test_run3(self):
    self.run_with_hosts(['localhost', 'localhost', 'localhost'])
