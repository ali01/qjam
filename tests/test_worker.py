from nose.tools import *
import json
import os
import subprocess
import sys

import qjam.worker.worker

# utils
from utils import source, encode, decode

# Test modules. These are serialized and sent to the worker to execute.
import constant
import no_poe
import raise_exc
import sum_dataset
import sum_params


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
    try:
      return json.loads(msg_str.strip())
    except ValueError, e:
      raise ValueError, 'error parsing message: "%s"' % msg_str.strip()
    assert_true('type' in msg)

  def read_error_string(self):
    '''Read a line from stdout, expecting to see an error.

    Returns:
      error string
    '''
    msg = self.read_message()
    assert_equals('error', msg['type'], 'expecting error message type')
    return msg['error']

  def write_message(self, msg):
    print '\nSending: %s' % json.dumps(msg)
    self._worker.stdin.write('%s\n' % json.dumps(msg))

  def write_command(self, cmd, data):
    data['type'] = cmd
    self.write_message(data)

  def send_refs(self, refs):
    msg = {'refs': refs}
    self.write_command('refs', msg)

  def send_task(self, module, params, dataset):
    msg = {'module': encode(source(module)),
           'params': encode(params),
           'dataset': dataset}
    self.write_command('task', msg)

  def read_result(self):
    '''Reads worker's stdout and expects a result message. Returns result.'''
    msg = self.read_message()
    assert_equal('result', msg['type'])
    assert_true('result' in msg)
    result = decode(msg['result'])
    return result

  def read_state(self):
    '''Reads worker's stdout and expects a state message. Returns message.'''
    msg = self.read_message()
    assert_equal('state', msg['type'])
    return msg

  def assert_status(self, msg, status):
    '''Asserts 'msg' is a state message with status 'status'.'''
    assert_true('status' in msg)
    assert_equal(status, msg['status'])

  def test_process(self):
    '''Make sure worker process is alive with proper communication handles.'''
    assert_not_equals(self._worker.stdin, None)
    assert_not_equals(self._worker.stdout, None)
    assert_not_equals(self._worker.stderr, None)

  def test_bad_message(self):
    '''Send a message without a type.'''
    self.write_message({'bogus_key': 1234})
    assert_true('missing type' in self.read_error_string())

  def test_bad_type(self):
    '''Send a message of an unknown type.'''
    self.write_command('bogus_command', {})
    assert_true('unexpected message type' in self.read_error_string())

  def test_bad_dataset(self):
    '''Send dataset that isn't a list of refs'''
    self.send_task(constant, (), None)
    assert_true('expected' in self.read_error_string())

  def test_incomplete_task(self):
    '''Send task messages without all required keys.'''
    c = encode(source(constant))
    msg1 = {'module': c,
            'params': encode(())}
    msg2 = {'module': c,
            'dataset': None}
    msg3 = {'dataset': None,
            'params': encode(())}

    for msg in (msg1, msg2, msg3):
      self.write_command('task', msg)
      assert_true('missing key' in self.read_error_string())

  def run_task(self, module, params, dataset):
    self.send_task(module, params, dataset)

    state_msg = self.read_state()
    # TODO(ms): This assumes worker has all refs.
    self.assert_status(state_msg, 'running')
    result = self.read_result()
    return result

  def test_constant(self):
    '''Return a constant number with a task.'''
    result = self.run_task(constant, None, [])
    assert_equals(42, result)

  def test_sum(self):
    '''Sum the list of params.'''
    params = [1, 2, 3, 6, 7, 9]
    result = self.run_task(sum_params, params, [])
    assert_equals(sum(params), result)

  def test_raise_exc(self):
    '''Run a callable that raises an exception.'''
    self.send_task(raise_exc, None, [])
    state_msg = self.read_state()
    assert_true('exception' in self.read_error_string())

  def test_multiple_tasks(self):
    '''Run multiple tasks on the same worker instance.'''
    self.test_constant()
    self.test_sum()
    self.test_constant()
    self.test_sum()

  def test_missing_refs(self):
    '''Start a task without having all refs on the worker.'''
    params = [1, 2, 3, 4]
    dataset = ['bogus_ref1', 'bogus_ref2']
    self.send_task(sum_params, params, dataset)
    state_msg = self.read_state()
    # Worker does not have given refs.
    self.assert_status(state_msg, 'blocked')
    assert_true('missing_refs' in state_msg)
    assert_equal(dataset, state_msg['missing_refs'])

  def test_no_poe(self):
    '''Send a task without a point of entry.'''
    self.send_task(no_poe, None, [])
    assert_true('point of entry' in self.read_error_string())

  def test_incomplete_refs_msg(self):
    '''Send refs message without 'refs' key.'''
    self.write_command('refs', {})
    assert_true('missing key' in self.read_error_string())

  def test_incorrect_refs_format(self):
    '''Send refs messages with bad types.'''
    self.send_refs(None)
    assert_true('expected' in self.read_error_string())
    self.send_refs([None])
    assert_true('expected' in self.read_error_string())
    self.send_refs([(None, None)])
    assert_true('expected' in self.read_error_string())
    self.send_refs([(1234, None)])
    assert_true('expected' in self.read_error_string())

  def test_sum_dataset_one_ref(self):
    '''Sum the elements of a dataset with one chunk.'''
    # Send task.
    dataset = ['ref1']
    chunk = [1, 2, 3, 4, 8, 33]
    self.send_task(sum_dataset, None, dataset)
    state_msg = self.read_state()
    self.assert_status(state_msg, 'blocked')

    # Send only missing ref.
    self.send_refs([(dataset[0], chunk)])

    # Ensure task is now running.
    state_msg = self.read_state()
    self.assert_status(state_msg, 'running')

    # Retrieve result.
    result = self.read_result()
    assert_equal(sum(chunk), result)
