"""DataSet objects are wrappers for some underlying data that expose an
interface for slicing up the underlying data into slices for single nodes."""

import numpy

def DataSet(o):
    if isinstance(o, BaseDataSet):
        return o
    elif isinstance(o, list) or isinstance(o, tuple):
        return ListDataSet(o)
    elif isinstance(o, numpy.ndarray):
        return NumPyMatrixDataSet(o)

class BaseDataSet(object):
    def slices(self, n_nodes):
        return [self.slice(n_nodes, i) for i in range(n_nodes)]
    
class ListDataSet(BaseDataSet):
    def __init__(self, _list):
        self.list = _list

    def slice(self, n_nodes, i):
        slice_size = (len(self.list)+n_nodes) / n_nodes # round up in division
        return self.list[slice_size*i:slice_size*(i+1)]

class NumPyMatrixDataSet(BaseDataSet):
    """Matrix whose rows are training examples."""
    def __init__(self, matrix):
        self.matrix = matrix

    def slice(self, n_nodes, i):
        nrows = numpy.size(self.matrix, 0)
        slice_rows = (nrows + n_nodes) / n_nodes # round up in division
        return self.matrix[slice_rows*i:slice_rows*(i+1)]
