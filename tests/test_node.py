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
            
class TestNode(NodeBaseTest, unittest.TestCase):
    def setUp(self):
        self.node = Node('localhost', 2000)
        self.node.clear_root()

class TestRemoteNode(NodeBaseTest, unittest.TestCase):
    def setUp(self):
        self.node = Node('127.0.0.1', 2000)
        self.node.clear_root()

