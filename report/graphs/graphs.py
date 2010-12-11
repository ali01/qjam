#!/usr/bin/env python

import sys
import math
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

class WorkersData(object):
  def __init__(self, workers, entries):
    self.workers_ = int(workers)
    self.entries_ = entries

  def workers(self):
    return self.workers_

  def entries(self):
    return len(self.entries_)

  def entry(self, index):
    return self.entries_[index]

  def entryIs(self, index, value):
    while len(self.entries_) <= index:
      self.entries_.append(0)
    self.entries_[index] = value

  def __getitem__(self, index):
    return self.entry(index)

  def __setitem__(self, index, value):
    self.entryIs(index, value)

  def __len__(self):
    return self.entries()


def plot_graph(data, title, filename=None, **kwds):
  if not filename:
    filename = title.lower().replace(' ', '_').replace('-', '_') + '.pdf'

  workers = map(WorkersData.workers, data)

  # defaults
  if 'labels' not in kwds:
    kwds['labels'] = ['NA'] * data[0].entries()
  if 'ylabel' not in kwds:
    kwds['ylabel'] = 'speedup (times faster)'
  if 'xlabel' not in kwds:
    kwds['xlabel'] = 'workers'
  if 'xticks' not in kwds:
    kwds['xticks'] = [0] + workers
  if 'xticks_loc' not in kwds:
    kwds['xticks_loc'] = [0, len(workers) + 2]

  plt.figure(figsize=(4, 4.5))

  for entry_num in range(0, data[0].entries()):
    X = range(1, len(workers) + 1)
    Y = map(lambda workerData: workerData[entry_num], data)
    plt.plot(X, Y, '-o', lw=1, label=kwds['labels'][entry_num])

  if 'show-single-core' in kwds and kwds['show-single-core']:
    plt.plot(kwds['xticks_loc'], [1, 1], '--', color='red', label='singe core')

  plt.xlabel(kwds['xlabel'])
  plt.ylabel(kwds['ylabel'])
  plt.xticks(kwds['xticks_loc'], kwds['xticks'])

  if 'ylim' in kwds:
    plt.ylim(kwds['ylim'])
  if 'xlim' in kwds:
    plt.xlim(kwds['xlim'])

  plt.legend(loc='upper left')
  plt.title(title)

  plt.savefig(filename, dpi=150)
  print 'plotted %s' % filename


def workerEntriesFromRuns(runs, worker):
  return map(lambda run: run[worker], runs)

def inverseEntriesFromRuns(runs, worker):
  return map(lambda run: 1.0/run[worker], runs)


def plot_iteration_mean_time(dataSet):
  runs = dataSet['iter']

  data = []
  data.append(WorkersData( 1, workerEntriesFromRuns(runs, 0))) # baseline
  data.append(WorkersData( 2, workerEntriesFromRuns(runs, 1)))
  data.append(WorkersData( 4, workerEntriesFromRuns(runs, 2)))
  data.append(WorkersData( 8, workerEntriesFromRuns(runs, 3)))
  data.append(WorkersData(16, workerEntriesFromRuns(runs, 4)))

  params = {}
  params['labels'] = ['1k', '10k', '100k']
  params['ylabel'] = 'percent running time'
  params['ylim'] = [0, 1.5]
  params['show-single-core'] = True
  plot_graph(data, 'Iteration Mean Time', **params)

def plot_iteration_mean_time_speedup(dataSet):
  runs = dataSet['iter']

  data = []
  data.append(WorkersData( 1, inverseEntriesFromRuns(runs, 0))) # baseline
  data.append(WorkersData( 2, inverseEntriesFromRuns(runs, 1)))
  data.append(WorkersData( 4, inverseEntriesFromRuns(runs, 2)))
  data.append(WorkersData( 8, inverseEntriesFromRuns(runs, 3)))
  data.append(WorkersData(16, inverseEntriesFromRuns(runs, 4)))

  params = {}
  params['xlim'] = [0.5, 5.5]
  params['ylim'] = [0, 8]
  params['labels'] = ['1k', '10k', '100k']
  params['show-single-core'] = True
  plot_graph(data, 'Iteration Mean Time Speedup', **params)

def plot_total_running_time(dataSet):
  runs = dataSet['total']

  data = []
  data.append(WorkersData( 1, workerEntriesFromRuns(runs, 0))) # baseline
  data.append(WorkersData( 2, workerEntriesFromRuns(runs, 1)))
  data.append(WorkersData( 4, workerEntriesFromRuns(runs, 2)))
  data.append(WorkersData( 8, workerEntriesFromRuns(runs, 3)))
  data.append(WorkersData(16, workerEntriesFromRuns(runs, 4)))

  params = {}
  params['labels'] = ['1k', '10k', '100k']
  params['ylabel'] = 'percent running time'
  params['ylim'] = [0, 1.5]
  params['show-single-core'] = True
  plot_graph(data, 'Total Running Time', **params)

def plot_total_running_time_speedup(dataSet):
  runs = dataSet['total']

  data = []
  data.append(WorkersData( 1, inverseEntriesFromRuns(runs, 0))) # baseline
  data.append(WorkersData( 2, inverseEntriesFromRuns(runs, 1)))
  data.append(WorkersData( 4, inverseEntriesFromRuns(runs, 2)))
  data.append(WorkersData( 8, inverseEntriesFromRuns(runs, 3)))
  data.append(WorkersData(16, inverseEntriesFromRuns(runs, 4)))

  params = {}
  params['xlim'] = [0.5, 5.5]
  params['ylim'] = [0, 8]
  params['labels'] = ['1k', '10k', '100k']
  params['show-single-core'] = True
  plot_graph(data, 'Total Running Time Speedup', **params)

def hundredk_iteration_vs_total(dataSet):
  runs = [dataSet['iter'][2], dataSet['total'][2]]

  data = []
  data.append(WorkersData( 1, workerEntriesFromRuns(runs, 0))) # baseline
  data.append(WorkersData( 2, workerEntriesFromRuns(runs, 1)))
  data.append(WorkersData( 4, workerEntriesFromRuns(runs, 2)))
  data.append(WorkersData( 8, workerEntriesFromRuns(runs, 3)))
  data.append(WorkersData(16, workerEntriesFromRuns(runs, 4)))

  params = {}
  params['labels'] = ['per iteration', 'total time']
  params['ylabel'] = 'percent running time'
  params['ylim'] = [0, 1.5]
  plot_graph(data, 'Per-Iteration vs Total Time', **params)

def hundredk_iteration_vs_total_speedup(dataSet):
  runs = [dataSet['iter'][2], dataSet['total'][2]]

  data = []
  data.append(WorkersData( 1, inverseEntriesFromRuns(runs, 0))) # baseline
  data.append(WorkersData( 2, inverseEntriesFromRuns(runs, 1)))
  data.append(WorkersData( 4, inverseEntriesFromRuns(runs, 2)))
  data.append(WorkersData( 8, inverseEntriesFromRuns(runs, 3)))
  data.append(WorkersData(16, inverseEntriesFromRuns(runs, 4)))

  params = {}
  params['xlim'] = [0.5, 5.5]
  params['ylim'] = [0, 8]
  params['labels'] = ['per iteration', 'total time']
  plot_graph(data, 'Per-Iteration vs Total Speedup', **params)


def readData():

  # hard coded for now.
  data = { 'iter' : [], 'total' : []}

  data['iter'].append([0.1458,  0.1752, 0.2634, 0.5339, 0.9969])
  data['iter'].append([0.7310,  0.3321, 0.3360, 0.5251, 1.0186])
  data['iter'].append([10.0282, 4.6782, 2.4858, 1.8046, 1.4376])

  data['total'].append([76, 92, 137, 275, 544])
  data['total'].append([370, 170, 173, 270, 529])
  data['total'].append([5030, 2350, 1253, 914, 703])

  normalizePatchSet = lambda pSet: map(lambda run: float(run)/pSet[0], pSet)
  normalizeDataSet = lambda dataSet: map(normalizePatchSet, dataSet)
  for dataSet in data:
    data[dataSet] = normalizeDataSet(data[dataSet])

  return data

def main():
  data = readData()

  plot_iteration_mean_time(data)
  plot_iteration_mean_time_speedup(data)
  plot_total_running_time(data)
  plot_total_running_time_speedup(data)
  hundredk_iteration_vs_total(data)
  hundredk_iteration_vs_total_speedup(data)

if __name__ == '__main__':
  main()

