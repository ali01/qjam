from nose.tools import *
import base64
import cPickle as pickle
import json
import os
import subprocess
import sys

import qjam.worker.worker

# Test modules. These are serialized and sent to the worker to execute.
import constant
import sum_params


def source(module):
  '''Return the source code for a given module object.'''
  filename = module.__file__
  filename = filename.replace('.pyc', '.py')
  with open(filename, 'r') as fh:
    return fh.read()


def encode(data):
  return base64.b64encode(pickle.dumps(data))


def decode(data):
  return pickle.loads(base64.b64decode(data))


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
    print '\nSending: %s' % json.dumps(msg)
    self._worker.stdin.write('%s\n' % json.dumps(msg))

  def write_command(self, cmd, data):
    data['type'] = cmd
    self.write_message(data)

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
    c = encode(source(constant))
    msg1 = {'module': c,
            'params': ()}
    msg2 = {'module': c,
            'dataset': None}
    msg3 = {'dataset': None,
            'params': ()}

    for msg in (msg1, msg2, msg3):
      self.write_command('task', msg)
      assert_true('missing key' in self.read_stderr())

  def test_simple_task(self):
    msg = {'module': encode(source(constant)),
           'params': encode(None),
           'dataset': []}
    self.write_command('task', msg)

    state_msg = self.read_message()
    assert_true('type' in state_msg)
    assert_equal('state', state_msg['type'])
    assert_true('status' in state_msg)
    assert_equal('running', state_msg['status'])

    result_msg = self.read_message()
    assert_true('result' in result_msg)
    result = decode(result_msg['result'])
    assert_equals(42, result)

  def test_sum(self):
    params = [1, 2, 3, 6, 7, 9]
    msg = {'module': encode(source(sum_params)),
           'params': encode(params),
           'dataset': []}
    self.write_command('task', msg)
    self.read_message()  # state
    result_msg = self.read_message()
    result = decode(result_msg['result'])
    assert_equals(sum(params), result)
