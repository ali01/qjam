from nose.tools import *

from qjam.master.master import Master
from qjam.master.remote_worker import RemoteWorker

# test modules
import constant
import sum_params

class TestMaster:
  def test_single_worker_simple(self):
    worker = RemoteWorker('localhost')
    master = Master([worker])

    assert_equals(42, master.run(constant))
    
    params = [1, 2, 3, 6, 7, 9]
    assert_equals(sum(params), master.run(sum_params, params))

  def test_dual_worker_simple(self):
    worker_1 = RemoteWorker('localhost')
    worker_2 = RemoteWorker('localhost')
    master = Master([worker_1, worker_2])

    assert_equals(84, master.run(constant))

    params = [1, 2, 3, 6, 7, 9]
    assert_equals(2 * sum(params), master.run(sum_params, params))
