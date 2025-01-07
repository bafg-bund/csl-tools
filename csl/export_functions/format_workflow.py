class FormatWorkflow:
    def __init__(self, inst, path_out, path_csl):
        self.inst = inst
        self.path_out = path_out
        self.path_csl = path_csl

    def export(self):
        raise NotImplementedError("Subclasses should implement this!")
