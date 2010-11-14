import unittest
from qjam.node import Node

class TestNode(unittest.TestCase):
    def test_name(self):
        self.assertEqual('localhost', Node('localhost').name)

    def test_default_root(self):
        self.assertEqual('/tmp/qjam', Node('localhost').root)

    def test_root(self):
        self.assertEqual('/tmp/qjam2', Node('localhost', root='/tmp/qjam2').root)

    def test_node_id(self):
        self.assertEqual('localhost_tmp_qjam', Node('localhost').node_id)

class TestLocalNode(unittest.TestCase):
    def setUp(self):
        self.localnode = Node('localhost', root='/tmp/qjam/')

    def tearDown(self):
        self.localnode.clear_root()
    
    def test_list_slices_empty(self):
        self.assertEqual([], self.localnode.slices.list())

    def test_slice_put(self):
        self.assertEqual([], self.localnode.slices.list())
        self.localnode.slices.put('slice1', 'hello')
        self.assertEqual(['slice1'], self.localnode.slices.list())
        self.localnode.slices.put('slice2', 'hello')
        self.assertEqual(['slice1', 'slice2'], sorted(self.localnode.slices.list()))

    def test_rpc_run(self):
        def func():
            return 7 * 11
        self.assertEqual(77, self.localnode.rpc_run(func))

    def test_task_status(self):
        self.assertEqual(False, self.localnode.task_status('job1'))
        self.localnode.task_status_set_finished('job1')
        self.assertEqual(True, self.localnode.task_status('job1'))
        self.localnode.task_status_set_unfinished('job1')
        self.assertEqual(False, self.localnode.task_status('job1'))

    def test_task_status_set_unfinished_no_raise_if_already_unfinished(self):
        self.localnode.task_status_set_unfinished('job1') # shouldn't raise
        
        
class TestRemoteNode(unittest.TestCase):
    pass
