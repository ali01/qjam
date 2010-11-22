from nose.tools import *
import base64
import cPickle as pickle
import json
import marshal
import os
import subprocess
import sys

import qjam.worker.worker


def constant(params, dataset):
  return 42


class Test_Worker:
  def setup(self):
    _path = qjam.worker.worker.__file__
    _path = _path.replace('.pyc', '.py')
    self._worker = subprocess.Popen(_path,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    bufsize=0)

  def teardown(self):
    self._worker.kill()

  def read_stderr(self):
    return self._worker.stderr.readline()

  def read_message(self):
    msg_str = self._worker.stdout.readline()
    return json.loads(msg_str.strip())

  def write_message(self, msg):
    self._worker.stdin.write('%s\n' % json.dumps(msg))

  def write_command(self, cmd, data):
    data['type'] = cmd
    self.write_message(data)

  def encode_callable(self, callable):
    return base64.b64encode(marshal.dumps(callable.func_code))

  def decode_result(self, data):
    return pickle.loads(base64.b64decode(data))

  def test_process(self):
    assert_not_equals(self._worker.stdin, None)
    assert_not_equals(self._worker.stdout, None)
    assert_not_equals(self._worker.stderr, None)

  def test_bad_message(self):
    self.write_message({'bogus_key': 1234})
    assert_true('ill-formed' in self.read_stderr())

  def test_bad_type(self):
    self.write_command('bogus_command', {})
    assert_true('unexpected message type' in self.read_stderr())

  def test_incomplete_task(self):
    c = self.encode_callable(constant)
    msg1 = {'callable': c,
            'params': ()}
    msg2 = {'callable': c,
            'dataset': None}
    msg3 = {'dataset': None,
            'params': ()}

    for msg in (msg1, msg2, msg3):
      self.write_command('task', msg)
      assert_true('missing key' in self.read_stderr())

  def test_simple_task(self):
    msg = {'callable': self.encode_callable(constant),
           'params': None,
           'dataset': None}
    self.write_command('task', msg)

    state_msg = self.read_message()
    assert_true('type' in state_msg)
    assert_equal('state', state_msg['type'])
    assert_true('status' in state_msg)
    assert_equal('running', state_msg['status'])

    result_msg = self.read_message()
    assert_true('result' in result_msg)
    result = self.decode_result(result_msg['result'])
    assert_equals(42, result)
