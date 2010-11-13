
class Slices(object):
    def __init__(self, node, root):
        self.node = node
        self.root = root

    def list(self):
        return self.node.fs_ls(self.root)
    
