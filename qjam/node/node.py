import threading, os, shutil, cPickle as pickle
from .slices import SliceStorage
from .task import NodeTaskThread

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

    def rpc_map_slice(self, func, slicename, params):
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

    def rpc_map_slice(self, func, slicename, params):
        slice = pickle.loads(self.slices.get(slicename))
        return self.rpc_run(func, slice, params)

class RemoteNode(BaseNode):
    pass
