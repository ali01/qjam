import os

class SliceStorage(object):
    def __init__(self, node, root):
        self.node = node
        self.root = root

    def __abspath_for_slicename(self, slicename):
        return os.path.join(self.root, slicename)
        
    def list(self):
        return self.node.fs_ls(self.root)

    def put(self, slicename, buf):
        self.node.fs_put(self.__abspath_for_slicename(slicename), buf)

    def get(self, slicename):
        return self.node.fs_get(self.__abspath_for_slicename(slicename))
    
