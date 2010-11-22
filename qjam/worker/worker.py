#!/usr/bin/python2.6
import json
import logging
import os
import sys


def read_message():
  line = sys.stdin.readline()
  line = line.strip()
  return line


def print_message(msg):
  print msg


def handle_message(msg):
  if msg['cmd'] == 'task':
    handle_task_message(msg)
  elif msg['cmd'] == 'refs':
    handle_refs_message(msg)
  else:
    logging.warning('unexpected command: %s' % msg['cmd'])


def process_message(msg):
  if 'cmd' not in msg:
    # Ill-formed message.
    raise ValueError

  print_message(msg)
  handle_message(msg)


def main():
  # Set up logging.
  _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  logging.basicConfig(level=logging.DEBUG, format=_fmt)

  while True:
    msg_str = read_message()
    try:
      msg = json.loads(msg_str)
      process_message(msg)
    except ValueError:
      logging.warning('received ill-formed message: %s' % msg_str)


if __name__ == '__main__':
  main()
