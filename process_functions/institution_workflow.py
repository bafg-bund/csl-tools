class InstitutionWorkflow:
    def __init__(self, path_data, path_csl):
        self.path_data = path_data
        self.path_csl = path_csl

    def process(self):
        raise NotImplementedError("Subclasses should implement this!")
