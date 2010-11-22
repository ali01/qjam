from nose.tools import *
import json
import os
import subprocess
import sys

import qjam.worker.worker


class Test_Worker:
  def setup(self):
    _path = qjam.worker.worker.__file__
    _path = _path.replace('.pyc', '.py')
    self._worker = subprocess.Popen(_path,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

  def teardown(self):
    self._worker.kill()

  def write_message(self, msg):
    self._worker.stdin.write('%s\n' % json.dumps(msg))

  def write_command(self, cmd, data):
    data['cmd'] = cmd
    self.write_message(data)

  def test_process(self):
    assert_not_equals(self._worker.stdin, None)
    assert_not_equals(self._worker.stdout, None)
    assert_not_equals(self._worker.stderr, None)

  def test_bad_message(self):
    self.write_message({'bogus_key': 1234})
    line = self._worker.stderr.readline()
    assert_true('ill-formed' in line)

  def test_bad_command(self):
    self.write_command('bogus_command', {})
    line = self._worker.stderr.readline()
    assert_true('unexpected command' in line)
