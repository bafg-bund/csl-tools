class FormatWorkflow:
    def __init__(self, path_out, path_csl, subset):
        self.path_out = path_out
        self.path_csl = path_csl
        self.subset = subset

    def export(self):
        raise NotImplementedError("Subclasses should implement this!")
