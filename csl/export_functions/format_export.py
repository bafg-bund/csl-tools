class FormatExport:
    def __init__(self, path_csl, path_out, subset):
        self.path_csl = path_csl
        self.path_out = path_out
        self.subset = subset

    def export(self):
        raise NotImplementedError("Subclasses should implement this!")
