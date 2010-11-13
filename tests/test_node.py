import unittest
from qjam.node import Node

class TestNode(unittest.TestCase):
    def test_name(self):
        self.assertEqual('localhost', Node('localhost').name)

    def test_default_root(self):
        self.assertEqual('/tmp/qjam', Node('localhost').root)

class TestLocalNode(unittest.TestCase):
    def setUp(self):
        self.localnode = Node('localhost', root='/tmp/qjam/')

    def tearDown(self):
        self.localnode.clear_root()
    
    def test_list_slices_empty(self):
        self.assertEqual([], self.localnode.slices.list())
        
class TestRemoteNode(unittest.TestCase):
    def test_data_slices(self):
        pass
