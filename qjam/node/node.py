import threading, os, shutil, cPickle as pickle

from .slices import SliceStorage

def Node(name, port=2000, root=None):
    root = root if root else "/tmp/qjam%d" % port
    return SSHRemoteNode(name, port, root)

class BaseNode(object):
    def __init__(self, name, port, root):
        self.name = name
        self.port = port
        self.root = root
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

        
    ########### Putting code file
        
    def __mapfunc_source(self, mapfunc):
        import inspect
        srclines = inspect.getsourcelines(mapfunc)[0]
        srclines[0] = srclines[0].lstrip() # un-indent first line
        return "\n".join(srclines)
        
    def put_code_file(self, job, task_name):
        # distribute mapfunc code file to node
        runner_py_abspath = self.path_for_file(job.name + '.py')
        mapfunc_src = self.__mapfunc_source(job.mapfunc)
        runner_py = """
import sys, pickle
from numpy import *

%(mapfunc_src)s

def main():
    slice_abspath = sys.argv[1]
    slice = None
    if slice_abspath:
        with open(slice_abspath, 'rb') as slicefile:
            slice = pickle.load(slicefile)
    mapfunc = %(mapfunc_name)s
    result = mapfunc(slice, %(params)r) # TODO: params
    with open(%(task_output_abspath)r, 'w') as outfile:
        pickle.dump(result, outfile)
    print "DONE"

main()
""" % dict(mapfunc_src=mapfunc_src, mapfunc_name=job.name, task_output_abspath=self.__task_output_file(task_name), params=job.params)

        self.fs_put(runner_py_abspath, runner_py)
        return runner_py_abspath

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
        runner_py_abspath = self.put_code_file(job, slicename)
        slice_abspath = self.slices.abspath_for_slicename(slicename)
        self.rpc_map_slice(runner_py_abspath, slice_abspath)
        return None # must poll node for return values of mapfunc

    # RPC interface implemented by {Local,SSHRemote}Node
    def rpc_run(self, func, *args, **kwargs):
        raise NotImplementedError

    def rpc_map_slice(self, func, slicename, params):
        raise NotImplementedError
    
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

class SSHRemoteNode(BaseNode):
    def __init__(self, name, port, root):
        self.__connected = False
        super(SSHRemoteNode, self).__init__(name, port, root)

    def __connect(self):
        import paramiko
        self.ssh = paramiko.SSHClient()
        self.ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        self.ssh.connect(self.name, username=os.getenv('USER'))
        self.sftp = self.ssh.open_sftp()
        self.__connected = True
        self.init_root()

    def rpc_map_slice(self, runner_py_abspath, slice_abspath):
        cmd = "python %s %s" % (runner_py_abspath, slice_abspath)
        self.ssh.exec_command(cmd)
        
    def fs_ls(self, dirname):
        if not self.__connected:
            self.__connect()
        return self.sftp.listdir(dirname)

    def fs_put(self, abspath, buf):
        if not self.__connected:
            self.__connect()
        f = self.sftp.open(abspath, 'wb')
        f.write(buf)
        f.close()

    def fs_mkdir(self, dirname):
        if not self.__connected:
            self.__connect()
        self.sftp.mkdir(dirname)

    def fs_get(self, abspath):
        if not self.__connected:
            self.__connect()
        f = self.sftp.open(abspath, 'rb')
        s = f.read()
        f.close()
        return s

    def fs_exists(self, abspath):
        if not self.__connected:
            self.__connect()
        try:
            self.sftp.stat(abspath)
            return True
        except IOError:
            return False

    def fs_rm(self, abspath):
        if not self.__connected:
            self.__connect()
        return self.sftp.unlink(abspath)

    def fs_rmdir(self, dirname):
        if not self.__connected:
            self.__connect()
        return self.sftp.rmdir(dirname)

    def close(self):
        if self.__connected:
            self.sftp.close()
            self.ssh.close()
            self.__connected = False
    
