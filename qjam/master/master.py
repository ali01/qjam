import os, inspect, time, cPickle as pickle
import pp

from qjam.node.node import LocalNode

POLL_INTERVAL = 0.5 # seconds

class Master(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def run(self, job):
        """Distributes data to nodes and then runs `job` on all nodes. Returns
        the sum of the nodes' responses."""

        # distribute data and run tasks
        nlocalnodes = sum([1 for n in self.nodes if isinstance(n, LocalNode)])
        job_server = pp.Server(nlocalnodes,
                               ppservers=tuple([n.host_port for n in self.nodes]),
                               secret='cs229qjam')
        tasks = []
        for i,node in enumerate(self.nodes):
            # distribute data
            slice = job.dataset.slice(len(self.nodes), i)
            slice_name = self.__slice_name(job.name, i)
            if slice_name not in node.slices.list():
                node.slices.put(slice_name, pickle.dumps(slice))

            # distribute mapfunc code file to node
            mapfunc_file = node.path_for_file(job.name + '.py')
            mapfunc_src = self.__mapfunc_source(job.mapfunc)
            node.fs_put(mapfunc_file, mapfunc_src)
            node.close()

            # run task
            slice_abspath = node.slices.abspath_for_slicename(slice_name)
            task = job_server.submit(node.mapfunc_for_task(),
                                     args=(job.name, mapfunc_file,
                                           slice_abspath, job.params,),
                                     modules=('pickle', 'imp'))
            tasks.append(task)

        # reduce task return values
        results = [t() for t in tasks]
        job_server.print_stats()
        return sum(results)

    def __slice_name(self, job_name, slice_num):
        return "%s_slice%dof%d" % (job_name, slice_num, len(self.nodes))

    def __mapfunc_source(self, mapfunc):
        srclines = inspect.getsourcelines(mapfunc)[0]
        srclines[0] = srclines[0].lstrip() # un-indent first line
        return "\n".join(srclines)
        
