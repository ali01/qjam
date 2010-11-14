import os, shutil, cPickle as pickle
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

    # Task interface
    #
    #     A task is an instance of a Job on a single node; a Job has many
    #     tasks. If the task status file exists, then the job is finished; if
    #     it does not exist, then the job is not finished.
    def __task_status_file(self, job_name):
        return os.path.join(self.root, "%s_%s_status" % (job_name, self.node_id))
    
    def task_status(self, job_name):
        return self.fs_exists(self.__task_status_file(job_name))

    def task_status_unfinished(self, job_name):
        self.fs_rm(self.__task_status_file(job_name))

    def task_status_finished(self, job_name):
        self.fs_put(self.__task_status_file(job_name), '')
    
    def run_task(self, job_name, func, slicename, params):
        self.task_status_unfinished(job_name)
        r = self.rpc_map(func, slicename, params)
        self.task_status_finished(job_name)
        return r
    
    # Abstract FS interface exposed to Slices
    def fs_ls(self, dirname):
        raise NotImplementedError

    def fs_put(self, abspath, buf):
        raise NotImplementedError

    def fs_get(self, abspath):
        raise NotImplementedError

    def fs_exists(self, abspath):
        raise NotImplementedError

    def fs_rm(self, abspath):
        raise NotImplementedError

    # RPC interface
    def rpc_run(self, func, *args, **kwargs):
        raise NotImplementedError

    def rpc_map(self, func, slicename, params):
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

    def fs_exists(self, abspath):
        return os.path.isfile(abspath)

    def fs_rm(self, abspath):
        return os.unlink(abspath)

    def rpc_run(self, func, *args, **kwargs):
        return func(*args, **kwargs)

    def rpc_map(self, func, slicename, params):
        slice = pickle.loads(self.slices.get(slicename))
        return self.rpc_run(func, slice, params)

class RemoteNode(BaseNode):
    pass
