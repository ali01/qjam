from .dataset import DataSet

class Job(object):
    def __init__(self, mapfunc, name=None, dataset=None, params=None):
        """Creates a new Job with map function `mapfunc`, name `name`, input
        dataset (training set) `dataset`, and parameters `params`."""
        self.mapfunc = mapfunc
        self.name = name
        self.dataset = DataSet(dataset)
        self.params = params

    def __str__(self):
        return self.name

