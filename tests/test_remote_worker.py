import logging
import sys
import time

from nose.tools import *

from qjam.dataset import DataSet
from qjam.master.remote_task_thread import RemoteTaskThread
from qjam.master.remote_worker import RemoteWorker
from qjam.master.remote_worker import RemoteWorkerError
from qjam.msg.task_msg import TaskMsg

# Test modules.
from modules import constant
from modules import crash
from modules import delayed_crash
from modules import multiply_sum_simple
from modules import sum_params


class TestRemoteWorker:
  def setup(self):
    _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=_fmt)
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

  def test_worker_crash_on_read(self):
    task_msg = TaskMsg(crash, params=42, dataset=None)
    assert_raises(RemoteWorkerError, self.remote_worker.taskIs, task_msg)

  def test_worker_crash_on_write(self):
    task_msg = TaskMsg(delayed_crash, params=42, dataset=None)
    result = self.remote_worker.taskIs(task_msg)
    assert_equals(42, result)
    time.sleep(0.5)  # wait for worker to die
    task_msg = TaskMsg(constant, params=42, dataset=None)
    assert_raises(RemoteWorkerError, self.remote_worker.taskIs, task_msg)


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
