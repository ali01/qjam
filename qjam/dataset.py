"""DataSet objects are wrappers for some underlying data that expose an
interface for slicing up the underlying data into slices for single nodes."""

def DataSet(o):
    if isinstance(o, BaseDataSet):
        return o
    elif isinstance(o, list) or isinstance(o, tuple):
        return ListDataSet(o)

class BaseDataSet(object):
    pass
    
class ListDataSet(BaseDataSet):
    def __init__(self, _list):
        self.list = _list

    def slice(self, n_nodes, i):
        slice_size = (len(self.list)+n_nodes) / n_nodes # round up in division
        return self.list[slice_size*i:slice_size*(i+1)]

    def slices(self, n_nodes):
        return [self.slice(n_nodes, i) for i in range(n_nodes)]
