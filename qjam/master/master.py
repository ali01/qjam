#!/usr/bin/python
import os
import threading
import base64
import json
import cPickle as pickle
import paramiko


class Master(worker_hostnames):
  def __init__(self, workers):
    self.__workers = workers

  def run(self, job):
    '''Distributes data to workers and then runs JOB on all workers.
       Returns the sum of the workers responses'''
    
    # distribute data and run tasks
    for i,worker in enumerate(self.__workers):
      # distribute data
      