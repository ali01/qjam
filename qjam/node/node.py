import os, shutil
from .slices import Slices

def Node(name, root='/tmp/qjam'):
    if name == 'localhost':
        return LocalNode(name, root)
    else:
        return RemoteNode(name, root)

class BaseNode(object):
    def __init__(self, name, root):
        self.name = name
        self.root = root
        self.init_root()
        self.slices = Slices(self, self.root)

    def init_root(self):
        raise NotImplementedError

    def clear_root(self):
        raise NotImplementedError

    # Abstract FS interface exposed to Slices
    def fs_ls(self, dirname):
        raise NotImplementedError

    def fs_put(self, abspath, buf):
        raise NotImplementedError

class LocalNode(BaseNode):
    def init_root(self):
        try:
            os.mkdir(self.root)
        except OSError:
            pass
        
    def clear_root(self):
        try:
            shutil.rmtree(self.root)
        except OSError:
            pass

    def fs_ls(self, dirname):
        return os.listdir(dirname)

    def fs_put(self, abspath, buf):
        f = open(abspath, 'wb')
        f.write(buf)
        f.close()

class RemoteNode(BaseNode):
    pass
