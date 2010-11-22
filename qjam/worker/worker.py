#!/usr/bin/python2.6
import base64
import cPickle as pickle
import imp
import json
import logging
import os
import sys
import tempfile
import types


def read_message_string():
  '''Read message from stdin.

  Returns:
    Message string without newline.
  '''
  line = sys.stdin.readline()
  line = line.strip()
  return line


def print_message(msg):
  '''Log a message object.

  Args:
    msg: message object

  Returns:
    None
  '''
  logging.debug('received message: %s' % msg)


def handle_message(msg):
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
    handle_task_message(msg)
  elif msg_type == 'refs':
    handle_refs_message(msg)
  else:
    exc_msg = 'unexpected message type: %s' % msg_type
    logging.warning(exc_msg)
    raise ValueError, exc_msg


def handle_task_message(msg):
  # Sanity check.
  for key in ('module', 'params', 'dataset'):
    if key not in msg:
      exc_msg = 'incomplete message: missing key "%s"' % key
      logging.warning(exc_msg)
      raise ValueError, exc_msg

  code = pickle.loads(base64.b64decode(msg['module']))

  # TODO(ms): Writing the code to a file is a hack to get the module
  #   object. Built-in functions like compile(), exec(), and eval() seem like a
  #   step in the right direction, but I haven't figured out a complete
  #   solution that doesn't involve the filesystem yet.
  temp_file = tempfile.NamedTemporaryFile()
  temp_file.write(code)
  temp_file.flush()
  module = imp.load_source('workermodule', temp_file.name)

  callable = getattr(module, 'run', None)
  params = pickle.loads(base64.b64decode(msg['params']))
  dataset = msg['dataset']

  # For now, assume no dataset.
  send_message('state', {'status': 'running'})

  # Run the callable.
  result = callable(params, dataset)

  # Send the result to the master.
  enc_result = base64.b64encode(pickle.dumps(result))
  send_message('result', {'result': enc_result})


def handle_refs_message(msg):
  pass


def send_error(err_str):
  '''Send an error message to stdout.

  Args:
    err_str: error string

  Returns:
    None
  '''
  send_message('error', {'error': err_str})


def send_message(msg_type, msg):
  msg['type'] = msg_type
  sys.stdout.write('%s\n' % json.dumps(msg))
  sys.stdout.flush()


def main():
  # Set up logging.
  _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  logging.basicConfig(level=logging.WARNING, format=_fmt)

  while True:
    msg_str = read_message_string()
    if not msg_str:
      return

    try:
      msg = json.loads(msg_str)
      handle_message(msg)
    except ValueError, e:
      send_error(str(e))


if __name__ == '__main__':
  main()
