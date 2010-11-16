import threading, os, shutil, cPickle as pickle
import paramiko

from .slices import SliceStorage
from .task import NodeTaskThread

def Node(name, port=2000, root=None):
    root = root if root else "/tmp/qjam%d" % port
    if name == 'localhost':
        return LocalNode(name, port, root)
    else:
        return RemoteNode(name, port, root)

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

    def init_root(self):
        if not self.fs_exists(self.root):
            self.fs_mkdir(self.root)

    def clear_root(self):
        if self.fs_exists(self.root):
            for e in self.fs_ls(self.root):
                self.fs_rm(os.path.join(self.root, e))
            self.fs_rmdir(self.root)

    # Task interface
    #
    #     A task is an instance of a Job on a single node; a Job has many
    #     tasks. If the task output file exists, then the task is finished; if
    #     it does not exist, then the task is not finished. The task name is
    #     the same as the slice name, since it represents an operation on that
    #     slice of data.
    def __task_output_file(self, task_name):
        return os.path.join(self.root, "%s_%s_output" % (task_name, self.node_id))
    
    def task_is_finished(self, task_name):
        return self.fs_exists(self.__task_output_file(task_name))

    def task_output_clear(self, task_name):
        if self.task_is_finished(task_name):
            self.fs_rm(self.__task_output_file(task_name))

    def task_output(self, task_name):
        return self.fs_get(self.__task_output_file(task_name))

    def task_output_set(self, task_name, buf):
        self.fs_put(self.__task_output_file(task_name), buf)
        
    def run_task(self, job, slicename):
        self.task_output_clear(slicename)
        nt = NodeTaskThread(self, job, slicename)
        nt.start()
        return None
    
    # Abstract FS interface implemented by {Local,Remote}Node
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

    # RPC interface implemented by {Local,Remote}Node
    def rpc_run(self, func, *args, **kwargs):
        raise NotImplementedError

    def rpc_map_slice(self, func, slicename, params):
        raise NotImplementedError

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

    def rpc_run(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def rpc_map_slice(self, func, slicename, params):
        slice = pickle.loads(self.slices.get(slicename))
        return self.rpc_run(func, slice, params)

class RemoteNode(BaseNode):
    def __init__(self, name, port, root):
        self.ssh = paramiko.SSHClient()
        self.ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        self.ssh.connect(name, username=os.getenv('USER'))
        self.sftp = self.ssh.open_sftp()
        super(RemoteNode, self).__init__(name, port, root)
        
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
    
    def rpc_run(self, func, *args, **kwargs):
        if kwargs:
            raise RuntimeError("kwargs not supported")
        import pp
        job_server = pp.Server(0, ppservers=(self.host_port,), secret='cs229qjam')
        f = job_server.submit(func, args)
        val = f()
        print val
        job_server.print_stats()
        return val
    
