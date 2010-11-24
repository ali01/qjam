#!/usr/bin/env python
from optparse import OptionParser # should use argparse for Python 2.7
import logging
import os
import sys

# Add parent directory to path.
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))

from qjam.dataset import DataSet
from qjam.master.remote_worker import RemoteWorker
from qjam.master.master import Master

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger('qjam')

def parse_args():
    parser = OptionParser(usage="%prog [opts] <module> <dataset> [params]")
    parser.add_option("-n", "--nodes", dest="nodes", default="localhost",
                      help="list of nodes, e.g. 'node1 node2'")
    parser.add_option("-q", "--quiet", dest="verbose",
                      action="store_false",
                      help="quiet (default is verbose)")
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.error("missing required args <module> <dataset>")
    return (options, args)

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
    options, args = parse_args()
    module_name = args[0]
    dataset_name = args[1]
    params_name = args[2] if len(args) == 3 else None

    # set up cluster
    workers = [RemoteWorker(host) for host in options.nodes.split()]
    # print_nodes(workers)
    master = Master(workers)

    # set up job
    # TODO: allow user to specify params - through a separate .py file?
    module = resolve_module_attr(module_name)
    params = resolve_module_attr(params_name) if params_name else None
    dataset = DataSet(resolve_module_attr(dataset_name))

    # run
    result = master.run(module, params, dataset)
    print result

if __name__ == "__main__":
    main()
