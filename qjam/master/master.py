
class Master(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def run(self, job):
        """Distributes data to nodes and then runs `job` on all nodes. Returns
        the sum of the nodes' responses."""
        result = 0
        for i,node in enumerate(self.nodes):
            result += node.rpc_run(job.mapfunc,
                                   job.dataset.slice(len(self.nodes), i),
                                   job.params)
        return result
