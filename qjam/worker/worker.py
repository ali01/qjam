#!/usr/bin/python2.6
import base64
import cPickle as pickle
import json
import logging
import marshal
import os
import sys
import types


def read_message():
  line = sys.stdin.readline()
  line = line.strip()
  return line


def print_message(msg):
  logging.debug('received message: %s' % msg)


def handle_message(msg):
  msg_type = msg['type']
  if msg_type == 'task':
    handle_task_message(msg)
  elif msg_type == 'refs':
    handle_refs_message(msg)
  else:
    logging.warning('unexpected message type: %s' % msg_type)


def handle_task_message(msg):
  # Sanity check.
  for key in ('callable', 'params', 'dataset'):
    if key not in msg:
      logging.warning('incomplete message: missing key "%s"' % key)
      return

  code = marshal.loads(base64.b64decode(msg['callable']))
  callable = types.FunctionType(code, globals(), 'foo')
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


def process_message(msg):
  if 'type' not in msg:
    # Ill-formed message.
    raise ValueError

  print_message(msg)
  handle_message(msg)


def send_message(msg_type, msg):
  msg['type'] = msg_type
  sys.stdout.write('%s\n' % json.dumps(msg))
  sys.stdout.flush()


def main():
  # Set up logging.
  _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  logging.basicConfig(level=logging.WARNING, format=_fmt)

  while True:
    msg_str = read_message()
    if not msg_str:
      return

    try:
      msg = json.loads(msg_str)
      process_message(msg)
    except ValueError, e:
      logging.warning('received ill-formed message: %s (%s)' % (msg_str, e))


if __name__ == '__main__':
  main()
