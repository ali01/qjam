import json
import logging
import os
import paramiko

from qjam.exceptions.remote_worker_error import RemoteWorkerError
from qjam.msg.base_msg import BaseMsg
from qjam.msg.error_msg import ErrorMsg, ErrorMsgFromDict
from qjam.msg.refs_msg import RefsMsg
from qjam.msg.result_msg import ResultMsg, ResultMsgFromDict
from qjam.msg.state_msg import StateMsg, StateMsgFromDict
from qjam.utils import module_path

REMOTE_CODE_PATH = os.path.join(os.sep, 'tmp', 'qjam-%s' % os.getenv('USER'))

# TODO(ali01): logging
# TODO(ali01): overlooked, but necessary, exception handling


class RemoteWorker(object):
  def __init__(self, host, port=22):
    # Adjust paramiko logging verbosity.
    _logger = paramiko.util.logging.getLogger('paramiko')
    _logger.setLevel(paramiko.common.WARNING)

    self.__host = host
    self.__port = port

    self.__init_worker_connection()
    self.__bootstrap_remote_worker()

    self.__task = None
    self.__result = None
    self.__logger = logging.getLogger('RemoteWorker')

  def __del__(self):
    self.__ssh_client.close()


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

    # transferring common code
    sftp = self.__ssh_client.open_sftp()

    remote_qjam_dir = os.path.join(REMOTE_CODE_PATH, 'qjam')
    remote_worker_dir = os.path.join(remote_qjam_dir, 'worker')
    remote_common_dir = os.path.join(remote_qjam_dir, 'common')

    self.__remote_mkdir(sftp, REMOTE_CODE_PATH)
    self.__remote_mkdir(sftp, remote_qjam_dir)
    self.__remote_mkdir(sftp, remote_worker_dir)
    self.__remote_mkdir(sftp, remote_common_dir)

    remote_qjam_init_path = os.path.join(remote_qjam_dir, '__init__.py')
    remote_worker_init_path = os.path.join(remote_worker_dir, '__init__.py')
    remote_common_init_path = os.path.join(remote_common_dir, '__init__.py')

    self.__remote_touch(remote_qjam_init_path)
    self.__remote_touch(remote_worker_init_path)
    self.__remote_touch(remote_common_init_path)

    from qjam.worker import worker
    remote_worker_path = os.path.join(remote_worker_dir, 'worker.py')
    sftp.put(module_path(worker), remote_worker_path)

    from qjam.common import reducing
    remote_reducer_path = os.path.join(remote_common_dir, 'reducing.py')
    sftp.put(module_path(reducing), remote_reducer_path)

    sftp.close()

    # executing worker code
    cmd = 'python2.6 %s' % (remote_worker_path)
    stdin, stdout, stderr = self.__ssh_client.exec_command(cmd);

    self.__r_stdin  = stdin
    self.__r_stdout = stdout
    self.__r_stderr = stderr


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

