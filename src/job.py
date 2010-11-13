
class Job(object):
    def __init__(self, mapfunc, name=None, trainset=None, params=None):
        """Creates a new Job with map function `mapfunc`, name `name`, training
        set `trainset`, and parameters `params`."""
        self.mapfunc = mapfunc
        self.name = name
        self.trainset = trainset
        self.params = params

    def __str__(self):
        return self.name

