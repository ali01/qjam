import os
import signal
import sys
import threading
import time


def mapfunc(params, dataset):
  lock = threading.Lock()
  with lock:
    t = threading.Thread(target=killer_thread, args=(lock,))
    t.daemon = True
    t.start()
  return 42


def killer_thread(lock):
  with lock:
    time.sleep(0.3)
    os.kill(os.getpid(), signal.SIGTERM)
