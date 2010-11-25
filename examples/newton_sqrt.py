def mapfunc(n, x):
    """Performs Newton's method to approximate sqrt(n)."""
    x = x[0]
    return x - (x*x - n)/(2*x)

if __name__ == "__main__":
    import sys
    from qjam import DataSet
    from qjam.master import Master, RemoteWorker

    if len(sys.argv) == 1:
        print "approximates sqrt(n)\nusage: %s <n> [<hostname> ...]" % sys.argv[0]
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

