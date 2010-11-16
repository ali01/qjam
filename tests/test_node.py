import unittest
from qjam.node import Node

class TestNode(unittest.TestCase):
    def test_name(self):
        self.assertEqual('localhost', Node('localhost').name)

    def test_default_port(self):
        self.assertEqual(2000, Node('localhost').port)

    def test_port(self):
        self.assertEqual(2123, Node('localhost', 2123).port)
        
    def test_default_root(self):
        self.assertEqual('/tmp/qjam2000', Node('localhost').root)

    def test_root(self):
        self.assertEqual('/tmp/qjam2', Node('localhost', root='/tmp/qjam2').root)

    def test_node_id(self):
        self.assertEqual('localhost:2144', Node('localhost', 2144).node_id)

class NodeBaseTest(object):
    def tearDown(self):
        self.node.clear_root()
    
    def test_list_slices_empty(self):
        self.assertEqual([], self.node.slices.list())

    def test_slice_put(self):
        self.assertEqual([], self.node.slices.list())
        self.node.slices.put('slice1', 'hello')
        self.assertEqual(['slice1'], self.node.slices.list())
        self.node.slices.put('slice2', 'hello')
        self.assertEqual(['slice1', 'slice2'], sorted(self.node.slices.list()))

    def test_rpc_run(self):
        def func():
            return 7 * 11
        self.assertEqual(77, self.node.rpc_run(func))

    def test_task_is_finished(self):
        self.assertEqual(False, self.node.task_is_finished('job1'))
        self.node.task_output_set('job1', 'somedata')
        self.assertEqual(True, self.node.task_is_finished('job1'))
        self.node.task_output_clear('job1')
        self.assertEqual(False, self.node.task_is_finished('job1'))

    def test_task_output_clear_no_raise_if_not_exists(self):
        self.node.task_output_clear('job_that_doesnt_exist') # shouldn't raise

class TestNode(NodeBaseTest, unittest.TestCase):
    def setUp(self):
        self.node = Node('localhost', 2001)

class TestRemoteNode(NodeBaseTest, unittest.TestCase):
    def setUp(self):
        self.node = Node('koi', 2002)

