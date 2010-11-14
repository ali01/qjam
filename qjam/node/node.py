import os, shutil
from .slices import SliceStorage

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
        self.slices = SliceStorage(self, self.root)

    @property
    def node_id(self):
        """Returns a unique identifier for this node that can be used as part
        of a filename."""
        return (self.name + self.root).replace('/', '_')
        
    def init_root(self):
        raise NotImplementedError

    def clear_root(self):
        raise NotImplementedError

    # Abstract FS interface exposed to Slices
    def fs_ls(self, dirname):
        raise NotImplementedError

    def fs_put(self, abspath, buf):
        raise NotImplementedError

    def fs_get(self, abspath):
        raise NotImplementedError

    # RPC interface
    def rpc_run(self, func):
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
        
    def fs_get(self, abspath):
        with open(abspath, 'rb') as f:
            return f.read()

    def rpc_run(self, func, *args, **kwargs):
        return func(*args, **kwargs)

class RemoteNode(BaseNode):
    pass
