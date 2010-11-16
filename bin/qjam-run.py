#!/usr/bin/env python
from optparse import OptionParser # should use argparse for Python 2.7
import sys, logging

from qjam import Node, Master, Job

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('qjam')

def parse_args():
    parser = OptionParser(usage="%prog [opts] <mapfunc> <dataset>")
    parser.add_option("-n", "--nodes", dest="nodes", default=["localhost"],
                      help="list of nodes, e.g. 'node1 node2'")
    parser.add_option("-q", "--quiet", dest="verbose",
                      action="store_false",
                      help="quiet (default is verbose)")
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("missing required args <mapfunc> <dataset>")
    return (options, args[0], args[1])

def print_nodes(nodes):
    logger.debug("qjam using %d nodes:" % len(nodes))
    for node in nodes:
        logger.debug("  %s"  % node)

def resolve_module_attr(name):
    """Returns the `someattr` attribute in `module1.module2` given the string
    'module1.module2.someattr` """
    hier, attr_name = name.rsplit('.', 1)
    __import__(hier)
    mod = sys.modules[hier]
    attr_val = getattr(mod, attr_name)
    return attr_val
        
def main():
    # parse args
    (options, mapfunc_name, dataset_name) = parse_args()

    # set up cluster
    nodes = [Node(host) for host in options.nodes]
    print_nodes(nodes)
    master = Master(nodes)

    # set up job
    # TODO: allow user to specify params - through a separate .py file?
    mapfunc = resolve_module_attr(mapfunc_name)
    dataset = resolve_module_attr(dataset_name)
    job_name = mapfunc_name.rsplit('.', 1)[1]
    job = Job(mapfunc, name=job_name, dataset=dataset, params=3)

    # run
    result = master.run(job)
    print result

if __name__ == "__main__":
    main()


