import unittest
import cPickle as pickle
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

    def __test_mapfunc_for_task_without_slice(self):
        def func(*ignore):
            return 7 * 11
        self.assertEqual(77, self.node.mapfunc_for_task(func)())

    def __test_mapfunc_for_task(self):
        def func(slice, x):
            return sum(slice) * x
        self.node.slices.put('onetwothree', pickle.dumps([1,2,3]))
        slice_abspath = self.node.slices.abspath_for_slicename('onetwothree')
        self.assertEqual(12, self.node.mapfunc_for_task(func)(slice_abspath, 2))
            
class TestNode(NodeBaseTest, unittest.TestCase):
    def setUp(self):
        self.node = Node('localhost', 2001)

class TestRemoteNode(NodeBaseTest, unittest.TestCase):
    def setUp(self):
        self.node = Node('koi', 2002)

