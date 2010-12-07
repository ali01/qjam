import sys, os, urllib2
from qjam import Master, DataSet
from qjam.master.remote_worker import RemoteWorker

def charcount(params, txtlines):
    cf = [0]*26
    for c in (''.join(txtlines)).lower():
        if c >= 'a' and c <= 'z':
            cf[ord(c)-ord('a')] += 1
    return cf
mapfunc = charcount

if __name__ == "__main__":
    workers = [RemoteWorker(h) for h in (sys.argv[1:] or ['localhost'])]
    url = os.getenv('TXTURL', 'http://stanford.edu/~sqs/qjam/shaks12.txt')
    txt = urllib2.urlopen(url).read().split("\n")
    cf = Master(workers).run(__import__('char_count'), None, DataSet(txt))
    for i,f in enumerate(cf):
        print "%s\t%d" % (chr(ord('a')+i), f)


