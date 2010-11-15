import cPickle as pickle
from threading import Thread

class NodeTaskThread(Thread):
    def __init__(self, node, job, slicename):
        Thread.__init__(self)
        self.node = node
        self.job = job
        self.slicename = slicename

    def run(self):
        r = self.node.rpc_map_slice(self.job.mapfunc,
                                    self.slicename, self.job.params)
        self.node.task_output_set(self.slicename, pickle.dumps(r))

