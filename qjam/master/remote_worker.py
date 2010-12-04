import json
import logging
import os
import subprocess

from qjam.exceptions.remote_worker_error import RemoteWorkerError
from qjam.msg.base_msg import BaseMsg
from qjam.msg.error_msg import ErrorMsg, ErrorMsgFromDict
from qjam.msg.refs_msg import RefsMsg
from qjam.msg.result_msg import ResultMsg, ResultMsgFromDict
from qjam.msg.state_msg import StateMsg, StateMsgFromDict
from qjam.utils import module_path

# TODO(ali01): logging
# TODO(ali01): overlooked, but necessary, exception handling


class RemoteWorker(object):
  def __init__(self, host, port=22):
    self.__logger = logging.getLogger('RemoteWorker')

    self.__host = host
    self.__port = port
    self.__user = os.getenv('QJAM_USER', None)

    self.__bootstrap_remote_worker()

    self.__task = None
    self.__result = None

  def __del__(self):
    self.__r_ssh.terminate()


  def taskIs(self, task_msg):
    '''runs task on remote worker;
       implements the master side of the wire protocol'''

    self.__task = task_msg
    self.__dataset = task_msg.dataset()

    # assigning task
    self.__send(task_msg)

    # waiting and processing running/blocking/result response
    try:
      msg = self.__recv()

      if msg['type'] == 'state':
        state_msg = StateMsgFromDict(msg)
        self.__process_state_msg(state_msg)

      elif msg['type'] == 'result':
        result_msg = ResultMsgFromDict(msg)
        self.__process_result_msg(result_msg);

    except RemoteWorkerError as e:
      raise e
      # todo(ali01): log error instead of raising e

    return self.__result


  def __process_state_msg(self, state_msg):
    if not isinstance(state_msg, StateMsg):
      raise TypeError

    if state_msg.status() == 'running':
      # remote has all necessary refs and is processing the task
      msg = self.__recv()
      if msg['type'] == 'result':
        result_msg = ResultMsgFromDict(msg)
        self.__process_result_msg(result_msg)

      else:
        exc_msg = '''expected message of type 'result'
                     but received message of type %s''' % msg['type']
        raise RemoteWorkerError(exc_msg)

    elif (state_msg.status() == 'blocked'):
      # send missing refs
      refs_msg = RefsMsg()
      for ref in state_msg.missing_refs():
        refs_msg.append(ref, self.__dataset.slice_data_from_hash(ref))
      self.__send(refs_msg)

      # expect state message
      msg = self.__recv()
      if msg['type'] == 'state':
        state_msg = StateMsgFromDict(msg)
        self.__process_state_msg(state_msg)
      else:
        exc_msg = '''expected message of type 'state'
                     but received message of type %s''' % msg['type']
        raise RemoteWorkerError(exc_msg)


  def __process_result_msg(self, result_msg):
    if (not isinstance(result_msg, ResultMsg)):
      raise TypeError

    self.__result = result_msg.result()


  def __bootstrap_remote_worker(self):
    '''Updates worker code on the remote machine and executes it.'''
    # Determine path to qjam package.
    import qjam
    local_pkg_path = os.path.dirname(qjam.__file__)

    # Construct remote paths. The 'qjam' package directory is placed here on
    # the remote side.
    user = self.__user or os.getenv('USER', 'nobody')
    remote_base_path = os.path.join(os.sep, 'tmp', 'qjam-%s' % user)
    remote_worker_dir = os.path.join(remote_base_path, 'qjam', 'worker')
    remote_worker_path = os.path.join(remote_worker_dir, 'worker.py')

    # Update code on remote machine.
    retcode = subprocess.call(['rsync', '-ru',
                               local_pkg_path, remote_base_path])
    self.__logger.debug('bootstrap rsync returned: %d' % retcode)
    if retcode != 0:
      raise RemoteWorkerError('failed to bootstrap %s: rsync returned %d' %
                              str(self), retcode)

    # Start remote worker process.
    python = os.getenv('QJAM_REMOTE_PYTHON', 'python2.6')
    if self.__user:
      host = '%s@%s' % (self.__user, self.__host)
    else:
      host = self.__host
    self.__r_ssh = subprocess.Popen(['ssh',
                                     '-p', str(self.__port),
                                     host,
                                     python,
                                     remote_worker_path],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

    self.__r_stdin  = self.__r_ssh.stdin
    self.__r_stdout = self.__r_ssh.stdout
    self.__r_stderr = self.__r_ssh.stderr


  def __send(self, msg):
    if (not issubclass(type(msg), BaseMsg)):
      raise TypeError

    self.__logger.debug('sending: %s' % msg.json_str())
    self.__r_stdin.write(('%s\n' % msg.json_str()))


  def __recv(self):
    try:
      line = self.__r_stdout.readline()
      self.__logger.debug('received: %s' % line)
      if line == '':
        self.__logger.info('%s crashed; reading stderr:' % str(self))
        stderr_line = self.__r_stderr.readline()[0:-1]
        while stderr_line:
          self.__logger.info('  | %s' % stderr_line)
          stderr_line = self.__r_stderr.readline()[0:-1]
        raise RemoteWorkerError('remote worker crashed')

      msg = json.loads(line)

      if msg['type'] == 'error':
        error_msg = ErrorMsgFromDict(msg)
        raise RemoteWorkerError(str(error_msg))

    except (KeyError, ValueError) as e:
      raise RemoteWorkerError('ill-formed incoming message from remote worker')

    return msg


  def __remote_mkdir(self, sftp_client, path):
    try:
      sftp_client.mkdir(path)
    except IOError:
      # log error: may fail if directory already exists
      pass


  def __remote_touch(self, path):
    self.__ssh_client.exec_command('touch -f %s' % path)

  def __str__(self):
    return "%s:%d" % (self.__host, self.__port)

