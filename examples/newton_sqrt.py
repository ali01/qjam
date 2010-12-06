def mapfunc(n, x):
    """Performs Newton's method to approximate sqrt(n)."""
    x = x[0]
    return x - (x*x - n)/(2*x)


def main():
    import logging
    import os
    import sys

    # Add parent directory to path.
    # Note that these imports cannot be at the top level because the worker
    # does not have these modules.
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '..'))
    from qjam import DataSet
    from qjam.master import Master, RemoteWorker

    _fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    logging.basicConfig(level=logging.WARNING, format=_fmt)

    if len(sys.argv) == 1:
        print "approximates sqrt(n)"
        print "usage: %s <n> [<hostname> ...]" % sys.argv[0]
        exit(1)
    n = float(sys.argv[1])
    cluster = sys.argv[2:]
    if not cluster:
        cluster = ['localhost']

    master = Master([RemoteWorker(host) for host in cluster])
    x0 = DataSet([float(10)])
    mod = sys.modules[__name__]

    eps = 0.0001
    xs = [float(10.0)]
    i = 1
    while True:
        x = master.run(mod, params=n, dataset=DataSet([xs[-1]]))
        dx = abs(x - xs[-1])
        xs.append(x)
        print "%d. %f (delta=%f)" % (i, x, dx)
        if dx < eps:
            break
        i += 1


if __name__ == "__main__":
    main()
