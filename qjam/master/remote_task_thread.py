import threading

from qjam.master.remote_worker import RemoteWorker
from qjam.msg.task_msg import TaskMsg

class RemoteTaskThread(threading.Thread):
  def __init__(self, remote_worker, task_msg):
    threading.Thread.__init__(self)
    if not isinstance(remote_worker, RemoteWorker):
      raise TypeError, 'expected object of type RemoteWorker'

    if not isinstance(task_msg, TaskMsg):
      raise TypeError, 'expected object of type TaskMsg'

    self.__remote_worker = remote_worker
    self.__task_msg = task_msg

  def run(self):
    self.__remote_worker.taskIs(self.__task_msg)

  def result(self):
    return self.__remote_worker.result()
