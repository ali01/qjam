import threading, os, shutil, cPickle as pickle

from .slices import SliceStorage

def Node(name, port=2000, root=None):
    root = root if root else "/tmp/qjam%d" % port
    if name == 'localhost':
        return LocalNode(name, port, root)
    else:
        return SSHRemoteNode(name, port, root)

class BaseNode(object):
    def __init__(self, name, port, root):
        self.name = name
        self.port = port
        self.root = root
        self.init_root()
        self.slices = SliceStorage(self, self.root)

    @property
    def host_port(self):
        """Returns `host`:`port` for this node."""
        return "%s:%d" % (self.name, self.port)
        
    @property
    def node_id(self):
        """Returns a unique identifier for this node that can be used as part
        of a filename."""
        return "%s_%d" % (self.name, self.port)

    def path_for_file(self, filename):
        """Returns the absolute path for `filename` under this node's root."""
        return os.path.join(self.root, filename)

    def init_root(self):
        if not self.fs_exists(self.root):
            self.fs_mkdir(self.root)

    def clear_root(self):
        if self.fs_exists(self.root):
            for e in self.fs_ls(self.root):
                self.fs_rm(os.path.join(self.root, e))
            self.fs_rmdir(self.root)
        self.init_root() # remake root dir

    def mapfunc_for_task(self):
        """Create a callable that we can send to a remote node for it to run,
        loading its locally stored data. The args are passed from the
        `job_server.submit` call in `Master.run."""
        def remote_mapfunc(job_name, mapfunc_file, slice_abspath=None, params=None):
                slice = None
                if slice_abspath:
                    with open(slice_abspath, 'rb') as slicefile:
                        slice = pickle.load(slicefile)
                mapfunc_module = imp.load_source('mapfunc_mod', mapfunc_file)
                mapfunc = getattr(mapfunc_module, job_name)
                return mapfunc(slice, params)
        return remote_mapfunc
    
    # Abstract FS interface implemented by {Local,SSHRemote}Node
    def fs_ls(self, dirname):
        raise NotImplementedError

    def fs_mkdir(self, dirname):
        raise NotImplementedError

    def fs_put(self, abspath, buf):
        raise NotImplementedError

    def fs_get(self, abspath):
        raise NotImplementedError

    def fs_exists(self, abspath):
        raise NotImplementedError

    def fs_rm(self, abspath):
        raise NotImplementedError

    def fs_rmdir(self, dirname):
        raise NotImplementedError

    def close(self):
        """Destructor for Node object. Only used for SSHRemoteNode, where it
        disconnects the SSH connection."""
        pass

    # Introspection
    def __str__(self):
        return "%s:%s" % (self.name, self.root)

class LocalNode(BaseNode):
    def fs_ls(self, dirname):
        return os.listdir(dirname)

    def fs_mkdir(self, dirname):
        os.mkdir(dirname)

    def fs_put(self, abspath, buf):
        f = open(abspath, 'wb')
        f.write(buf)
        f.close()
        
    def fs_get(self, abspath):
        with open(abspath, 'rb') as f:
            return f.read()

    def fs_exists(self, abspath):
        return os.path.exists(abspath)

    def fs_rm(self, abspath):
        return os.unlink(abspath)

    def fs_rmdir(self, dirname):
        return os.rmdir(dirname)

class SSHRemoteNode(BaseNode):
    def __init__(self, name, port, root):
        import paramiko
        self.ssh = paramiko.SSHClient()
        self.ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        self.ssh.connect(name, username=os.getenv('USER'))
        self.sftp = self.ssh.open_sftp()
        super(SSHRemoteNode, self).__init__(name, port, root)
        
    def fs_ls(self, dirname):
        return self.sftp.listdir(dirname)

    def fs_put(self, abspath, buf):
        f = self.sftp.open(abspath, 'wb')
        f.write(buf)
        f.close()

    def fs_mkdir(self, dirname):
        self.sftp.mkdir(dirname)

    def fs_get(self, abspath):
        f = self.sftp.open(abspath, 'rb')
        s = f.read()
        f.close()
        return s

    def fs_exists(self, abspath):
        try:
            self.sftp.stat(abspath)
            return True
        except IOError:
            return False

    def fs_rm(self, abspath):
        return self.sftp.unlink(abspath)

    def fs_rmdir(self, dirname):
        return self.sftp.rmdir(dirname)

    def close(self):
        self.sftp.close()
        self.ssh.close()
    
