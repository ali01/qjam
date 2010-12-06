#!/usr/bin/env python2.6
import base64
import cPickle as pickle
import hashlib
import imp
import inspect
import json
import logging
import os
import signal
import sys
import tempfile

# Adjust path to have access to other qjam code.
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..', '..'))

from qjam.common import reducing


class RefStore(object):
  def __init__(self):
    self._refs = {}

  def refs(self):
    '''Get number of refs in store.

    Returns:
      integer
    '''
    return len(self._refs.keys())

  def ref(self, name):
    '''Get ref by given name.

    Returns:
      object or None if not found
    '''
    return self._refs.get(name, None)

  def ref_is(self, name, value):
    '''Store a ref. An existing ref of the same name will be overwritten.

    Args:
      name: string name of ref
      value: object

    Returns:
      None
    '''
    self._refs[name] = value

  def missing(self, refs):
    '''Get list of refs not in the store.

    Args:
      refs: list of refs

    Returns:
      subset of 'refs' not in the store
    '''
    subset = []
    for ref in refs:
      if ref not in self._refs:
        subset.append(ref)
    return subset


class Task(object):
  def __init__(self, module, params, dataset):
    self._module = module
    self._params = params
    self._dataset = dataset

    # Compute id.
    hash = hashlib.sha1()
    # TODO(ms): This inspect hack depends on the code for the module being
    #   available when the Task is constructed. Usually this is the case, but
    #   if the code is stored in a temporary file that is closed and deleted
    #   before the Task object is constructed (but after the module is compiled
    #   and loaded into memory), this call will fail with a fairly general
    #   error message ("could not get source code").
    hash.update(inspect.getsource(self._module))
    hash.update(str(self._params))
    hash.update(str(self._dataset))
    self._id = hash.hexdigest()

  def __eq__(self, other):
    return (self.id() == other.id())

  def __ne__(self, other):
    return not self.__eq__(other)

  def module(self):
    return self._module

  def params(self):
    return self._params

  def dataset(self):
    return self._dataset

  def id(self):
    '''Get Unique ID for this task.

    Returns:
      ID string
    '''
    return self._id


class TaskQueue(object):
  def __init__(self, refstore):
    self._queue = []
    self._refstore = refstore

  def task_is(self, task):
    '''Add new task to the queue.

    Args:
      task: Task object

    Returns:
      None
    '''
    self._queue.append(task)

  def task_del(self, task):
    '''Remove a task from the queue.

    Args:
      task: Task object to remove

    Returns:
      None
    '''
    self._queue.remove(task)

  def dequeue(self):
    '''Get and remove next unblocked Task object from queue. If all tasks are
    blocked (waiting on refs), None is returned.

    Returns:
      Task object or None
    '''
    to_return = None
    for task in self._queue:
      missing = self._refstore.missing(task.dataset())
      if not missing:
        to_return = task
        break
      else:
        logging.info('task %s is missing: %s' % (task.id(), str(missing)))

    if to_return is not None:
      self.task_del(to_return)
    return to_return


class Worker(object):
  def __init__(self, input, output, refstore=None):
    '''Initialize the worker.

    Args:
      input: file object for Worker's input
      output: file object for Worker's output
      refstore: RefStore object for object storage
    '''
    self._input = input
    self._output = output
    if refstore is None:
      refstore = RefStore()
    self._refstore = refstore
    self._taskqueue = TaskQueue(self._refstore)

  def _read_message_string(self):
    '''Read message from input stream.

    Returns:
      Message string without newline.
    '''
    line = self._input.readline().strip()
    return line

  def _handle_message(self, msg):
    '''Dispatch a message object to the appropriate handler.

    Args:
      msg: message object

    Raises:
      ValueError if message is ill-formed or contains an unexpected type.

    Returns:
      None
    '''
    print_message(msg)

    if 'type' not in msg:
      # Ill-formed message.
      logging.warning('message is missing type, ignoring')
      raise ValueError, 'message is missing type'

    msg_type = msg['type']
    if msg_type == 'task':
      self._handle_task_message(msg)
    elif msg_type == 'refs':
      self._handle_refs_message(msg)
    else:
      exc_msg = 'unexpected message type: %s' % msg_type
      logging.warning(exc_msg)
      raise ValueError, exc_msg

  def _handle_task_message(self, msg):
    '''Message handler for "task" messages.

    Args:
      msg: mesage object

    Raises:
      ValueError on incomplete messages

    Returns:
      None
    '''
    # Sanity check.
    for key in ('module', 'params', 'dataset'):
      if key not in msg:
        exc_msg = 'incomplete message: missing key "%s"' % key
        logging.warning(exc_msg)
        raise ValueError, exc_msg

    # Python source code for the runnable module.
    code = pickle.loads(base64.b64decode(msg['module']))

    # TODO(ms): Writing the code to a file is a hack to get the module
    #   object. Built-in functions like compile(), exec(), and eval() seem like
    #   a step in the right direction, but I haven't figured out a complete
    #   solution that doesn't involve the filesystem yet.
    temp_file = tempfile.NamedTemporaryFile()
    temp_file.write(code)
    temp_file.flush()
    # Don't close the temp_file yet; need to load it below.

    # Load the module object.
    module = imp.load_source('workermodule', temp_file.name)
    if not getattr(module, 'mapfunc', None):
      exc_msg = 'given module is missing "mapfunc" point of entry'
      logging.warning(exc_msg)
      raise ValueError, exc_msg

    # Params are passed directly to the callable.
    params = msg['params']
    if not isinstance(params, unicode):
      exc_msg = 'expected base64-encoded pickled object for params'
      logging.warning(exc_msg)
      raise ValueError, exc_msg
    params = pickle.loads(base64.b64decode(msg['params']))

    # The dataset is a list of refs.
    dataset = msg['dataset']
    if not isinstance(dataset, list):
      exc_msg = 'expected list of refs for dataset'
      logging.warning(exc_msg)
      raise ValueError, exc_msg

    # Add task to queue.
    task = Task(module, params, dataset)
    self._taskqueue.task_is(task)

    # Determine if any refs are missing.
    missing = self._refstore.missing(dataset)
    if missing:
      self._send_message('state', status='blocked', missing_refs=missing)

  def _handle_refs_message(self, msg):
    # Sanity check.
    if 'refs' not in msg:
      exc_msg = 'incomplete message: missing key "refs"'
      logging.warning(exc_msg)
      raise ValueError, exc_msg
    refs = msg['refs']
    if not isinstance(refs, list):
      exc_msg = 'expected list of tuples for refs'
      logging.warning(exc_msg)
      raise ValueError, exc_msg

    # Ensure all refs are (str, encoded obj).
    for tup in refs:
      if (not isinstance(tup, list) or
          len(tup) != 2 or
          not isinstance(tup[0], unicode) or
          not isinstance(tup[1], unicode)):
        exc_msg = 'expected list of [str, obj] for refs'
        logging.warning(exc_msg)
        raise ValueError, exc_msg

    # Store new refs.
    for (ref, obj) in refs:
      obj = pickle.loads(base64.b64decode(obj))
      self._refstore.ref_is(ref, obj)

  def _process_tasks(self):
    task = self._taskqueue.dequeue()
    while task is not None:
      self._process_task(task)
      task = self._taskqueue.dequeue()

  def _process_task(self, task):
    self._send_message('state', id=task.id(), status='running')

    # Entry point in the module.
    callable = getattr(task.module(), 'mapfunc')

    # Run the callable.
    # All exceptions in the callable will cause immediate return from this
    # function. No 'result' messages are sent in this case. The assumption is
    # that if an exception occurred during the processing of any chunk, the
    # result is invalid and is therefore not returned.
    dataset = task.dataset()
    if len(dataset) == 0:
      try:
        result = self._run_callable(callable, task.params(), dataset)
      except Exception, e:
        self._send_error('callable raised exception: %s' % str(e))
        return
    else:
      results = []
      for ref in dataset:
        chunk = self._refstore.ref(ref)
        try:
          result = self._run_callable(callable, task.params(), chunk)
        except Exception, e:
          self._send_error('callable raised exception: %s' % str(e))
          return
        results.append(result)

      # In-mapper reducing.
      if results:
        result = reduce(reducing.default_reduce, results)
      else:
        result = None

    # Send the result to the master.
    enc_result = base64.b64encode(pickle.dumps(result))
    self._send_message('result', id=task.id(), result=enc_result)

  def _run_callable(self, callable, params, dataset):
    '''Runs the callable.

    Args:
      params: params to pass to the callable
      dataset: dataset to pass to the callable

    Raises:
      any exception the callable might raise

    Returns:
      result returned by callable
    '''
    # Redirect stdout to stderr when running the callable.
    old_stdout = sys.stdout
    sys.stdout = sys.stderr

    result = callable(params, dataset)

    # Restore old stdout.
    sys.stdout = old_stdout

    return result

  def _send_error(self, err_str):
    '''Send an error message to stdout.

    Args:
      err_str: error string

    Returns:
      None
    '''
    self._send_message('error', error=err_str)

  def _send_message(self, msg_type, **kwargs):
    '''Send a message to output stream.

    Args:
      msg_type: message type ('error', 'state', 'result')
      msg: dictionary of other parameters to include in outgoing message

    Returns:
      None
    '''
    msg = kwargs
    msg['type'] = msg_type
    self._output.write('%s\n' % json.dumps(msg))
    self._output.flush()

  def run(self):
    '''Entry point into the worker. Processes and responds to incoming messages
    forever. Does not return.
    '''
    while True:
      # Read incoming message.
      msg_str = self._read_message_string()
      if not msg_str:
        return

      # Process message.
      try:
        msg = json.loads(msg_str)
      except ValueError, e:
        self._send_error('error parsing incoming message')
      else:
        try:
          self._handle_message(msg)
        except ValueError, e:
          self._send_error(str(e))

      # Run any ready tasks.
      self._process_tasks()


def signal_handler(signum, frame):
  logging.critical('received signal %d; exiting.' % signum)
  sys.exit(-1)


def print_message(msg):
  '''Log a message object.

  Args:
    msg: message object

  Returns:
  None
  '''
  logging.debug('received message: %s' % msg)


def main():
  # Writing too much data to stderr will cause the worker to block if the other
  # side does not read the stderr handle.
  log_level = logging.CRITICAL
  if len(sys.argv) > 1 and sys.argv[1] == '-d':
    log_level = logging.DEBUG

  # Set up logging.
  _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  logging.basicConfig(level=log_level, format=_fmt)

  # Signal handler.
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGALRM, signal_handler)

  # Create a Worker and attach it to the stdin and stdout streams.
  worker = Worker(sys.stdin, sys.stdout)
  worker.run()


if __name__ == '__main__':
  main()
