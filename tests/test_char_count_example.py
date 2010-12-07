import unittest, subprocess, os

class TestCharCountExample(unittest.TestCase):
  def __get_output(self, cmd, **kw):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, **kw).communicate()[0]

  def run_with_hosts(self, hosts):
    cmd = ['python', 'examples/char_count.py']
    cmd += hosts
    env = dict(os.environ)
    env['TXTURL'] = 'http://stanford.edu/~sqs/qjam/shaks12-excerpt.txt'
    output = self.__get_output(cmd, env=env)
    print output
    self.assertTrue('q\t5' in output)

  def test_run1(self):
    self.run_with_hosts(['localhost'])

  def test_run2(self):
    self.run_with_hosts(['localhost', 'localhost'])
