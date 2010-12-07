import subprocess, sys, time, re

if len(sys.argv) != 5:
    print "  usage: %s <module .py> <cluster> <nworkers> <jobargs>" % sys.argv[0]
    print
    print "example: %s example.py   corn1,... 1,2,4,8 1000,10000" % \
        sys.argv[0]
    print "example: %s examples/newton_sqrt.py localhost 1,1 12345" % \
        sys.argv[0]
    print "example: %s examples/sparse_autoencoder.py corn12,corn13" \
        " 2 1000" % sys.argv[0]
    exit(1)

pyfile   = sys.argv[1]
cluster  = sys.argv[2].split(',')
nworkers = [int(n) for n in sys.argv[3].split(',')]
jobargs  = sys.argv[4].split(',')
stats = []

for nw in nworkers:
    for arg in jobargs:
        cmd = ['python', pyfile]
        cmd.append(arg)
        cmd += cluster[:nw]
        sys.stderr.write("--> %s\n" % ' '.join(cmd))

        t0 = time.time()
        qjam = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = qjam.communicate()
        t1 = time.time()

        iterts = [float(f) for f in
                  re.findall(r'elapsed time: ([.\d]+)s', err)]
        #for i,it in enumerate(iterts):
        #    print "   iter %d:\t %f" % (i,it)

        mystats = {'label': 'nworkers=%d,args=%s' % (nw,arg),
                   'niter': len(iterts),
                   'itermean': sum(iterts)/len(iterts),
                   'itermax': max(iterts),
                   'itermin': min(iterts),
                   'itersum': sum(iterts),
                   'master': t1-t0}
        stats.append(mystats)

        for k,v in sorted(mystats.items()):
            if k == 'label': continue
            print "%s\t%s\t%s" % (mystats['label'], k, v)


sys.stderr.write(
    "\nnote: master time includes master overhead; itersum is " \
    "just the sum of the times it took all the workers to return.\n" \
    "note2: the logging level must be set to logging.INFO in" \
    "your job file or  else this script can't determine iteration times.\n"
)
