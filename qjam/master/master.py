import cPickle as pickle

class Master(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def run(self, job):
        """Distributes data to nodes and then runs `job` on all nodes. Returns
        the sum of the nodes' responses."""
        self.__distribute_data(job.name, job.dataset)
        
        result = 0
        for i,node in enumerate(self.nodes):
            result += node.rpc_map(job.mapfunc,
                                   self.__slice_name(job.name, i),
                                   job.params)
        return result

    def __slice_name(self, job_name, slice_num):
        return "%s_slice%d" % (job_name, slice_num)

    def __distribute_data(self, job_name, dataset):
        for i,node in enumerate(self.nodes):
            slice = dataset.slice(len(self.nodes), i)
            slice_name = self.__slice_name(job_name, i)
            node.slices.put(slice_name, pickle.dumps(slice))
