import json
import logging
import os
import paramiko
import threading

from qjam.msg.base_msg import BaseMsg
from qjam.msg.state_msg import StateMsg, StateMsgFromDict
from qjam.msg.result_msg import ResultMsg, ResultMsgFromDict
from qjam.exceptions.remote_worker_error import RemoteWorkerError

# TODO(ali01): remove hard coded path; use source of module instead
LOCAL_WORKER_PATH  = os.path.join('..', 'qjam', 'worker', 'worker.py')
REMOTE_WORKER_PATH = os.path.join(os.sep, 'tmp', 'worker.py')

# TODO(ali01): logging
# TODO(ali01): overlooked, but necessary, exception handling

class RemoteWorker(object):
  def __init__(self, host, port=22):
    self.__host = host
    self.__port = port

    self.__init_worker_connection()
    self.__bootstrap_remote_worker()


  def taskIs(self, task_msg):
    '''runs task on remote worker;
       implements the master side of the wire protocol'''

    # assigning task
    self.__send(task_msg)

    # waiting and processing running/blocking/result response
    try:
      msg = self.__recv()

      if (msg['type'] == 'state'):
        state_msg = StateMsgFromDict(msg)
        self.__process_state_msg(state_msg)

      elif (msg['type'] == 'result'):
        result_msg = ResultMsgFromDict(msg)
        self.__process_result_msg(result_msg);

    except RemoteWorkerError as e:
      raise e
      # todo(ali01): log error instead of raising e

  def result(self):
    return self.__result

  def __init_worker_connection(self):
    '''initializes ssh client for worker connection'''

    hosts_path = os.path.expanduser(os.path.join('~', '.ssh', 'known_hosts'))
    self.__ssh_client = paramiko.SSHClient()
    self.__ssh_client.load_host_keys(hosts_path)
    self.__ssh_client.connect(self.__host, self.__port,
                              username=os.getenv('USER'))


  def __bootstrap_remote_worker(self):
    '''transfers worker/worker.py to the remote worker executes it on the
       remote'''

    # transferring worker code
    sftp = self.__ssh_client.open_sftp()
    sftp.put(LOCAL_WORKER_PATH, REMOTE_WORKER_PATH)

    # executing worker code
    cmd = 'python %s' % (REMOTE_WORKER_PATH)
    stdin, stdout, stderr = self.__ssh_client.exec_command(cmd);

    self.__r_stdin  = stdin
    self.__r_stdout = stdout
    self.__r_stderr = stderr


  def __process_state_msg(self, state_msg):
    if (not isinstance(state_msg, StateMsg)):
      raise TypeError

    if (state_msg.status() == 'running'):
      # remote has all necessary refs and is processing the task
      msg = self.__recv()
      if (msg['type'] == 'result'):
        result_msg = ResultMsgFromDict(msg)
        self.__process_result_msg(result_msg)

      else:
        raise RemoteWorkerError('''expected message of type 'result'
                                   but received message of type %s''' %
                                msg['type'])

    elif (msg['type'] == 'blocking'):
      # todo(ali01): send missing refs
      pass


  def __process_result_msg(self, result_msg):
    if (not isinstance(result_msg, ResultMsg)):
      raise TypeError

    self.__result = result_msg.result()


  def __send(self, msg):
    if (not issubclass(type(msg), BaseMsg)):
      raise TypeError

    self.__r_stdin.write(('%s\n' % msg.json_str()))


  def __recv(self):
    try:
      msg = json.loads(self.__r_stdout.readline())

      if (msg['type'] == 'error'):
        error_msg = ErrorMsgFromDict(msg)
        raise RemoteWorkerError(str(error_msg))

    except (KeyError, ValueError) as e:
      raise RemoteWorkerError("ill-formed incoming message from remote worker")

    return msg

