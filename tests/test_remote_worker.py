from nose.tools import *

from qjam.master.remote_worker import RemoteWorker
from qjam.msg.task_msg import TaskMsg

# test modules
import constant
import sum_params

class TestRemoteWorker:
  def setup(self):
    self.remote_worker = RemoteWorker('localhost')

  def test_task_constant(self):
    task_msg = TaskMsg(constant, params=None, dataset=[])
    self.remote_worker.taskIs(task_msg)
    assert_equals(42, self.remote_worker.result())


  def test_task_sum(self):
    params = [1, 2, 3, 6, 7, 9]
    task_msg = TaskMsg(sum_params, params, dataset=[])
    self.remote_worker.taskIs(task_msg)
    assert_equals(sum(params), self.remote_worker.result())
