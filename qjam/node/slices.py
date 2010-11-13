import os

class SliceStorage(object):
    def __init__(self, node, root):
        self.node = node
        self.root = root

    def list(self):
        return self.node.fs_ls(self.root)

    def put(self, slicename, buf):
        abspath = os.path.join(self.root, slicename)
        self.node.fs_put(abspath, buf)
    
