from nose.tools import *

from qjam.dataset import DataSet
from qjam.master.remote_task_thread import RemoteTaskThread
from qjam.master.remote_worker import RemoteWorker
from qjam.msg.task_msg import TaskMsg

# test modules
import constant
import sum_params
from modules import multiply_sum_simple

class TestRemoteWorker:
  def setup(self):
    self.remote_worker = RemoteWorker('localhost')

  def test_task_constant(self):
    task_msg = TaskMsg(constant, params=None, dataset=None)
    result = self.remote_worker.taskIs(task_msg)
    assert_equals(42, result)

  def test_task_sum(self):
    params = [1, 2, 3, 6, 7, 9]
    task_msg = TaskMsg(sum_params, params, dataset=None)
    result = self.remote_worker.taskIs(task_msg)
    assert_equals(sum(params), result)

  def test_multiply_sum_simple(self):
    list = range(0,100)
    dataset = DataSet(list, slice_size=5)
    assert_equals(20, len(dataset))

    task_msg = TaskMsg(multiply_sum_simple, params=3, dataset=dataset)
    result = self.remote_worker.taskIs(task_msg)
    assert_equals(14850, result)

class TestRemoteTaskThread:
  def setup(self):
    self.remote_worker = RemoteWorker('localhost')

  def test_task_constant(self):
    task_msg = TaskMsg(constant, params=None, dataset=None)
    task_thread = RemoteTaskThread(self.remote_worker, task_msg);
    task_thread.start()
    task_thread.join()
    assert_equals(42, task_thread.result())

  def test_task_sum(self):
    params = [1, 2, 3, 6, 7, 9]
    task_msg = TaskMsg(sum_params, params, dataset=None)
    task_thread = RemoteTaskThread(self.remote_worker, task_msg);
    task_thread.start()
    task_thread.join()
    assert_equals(sum(params), task_thread.result())

  def test_multiply_sum_simple(self):
    list = range(0,100)
    dataset = DataSet(list, slice_size=4)
    assert_equals(25, len(dataset))

    task_msg = TaskMsg(multiply_sum_simple, params=3, dataset=dataset)
    task_thread = RemoteTaskThread(self.remote_worker, task_msg)
    task_thread.start()
    task_thread.join()
    assert_equals(14850, task_thread.result())
