class OperationWorkflow:
    def __init__(self, path_csl):
        self.path_csl = path_csl

    def rtscan(self):
        raise NotImplementedError("Subclasses should implement this!")
