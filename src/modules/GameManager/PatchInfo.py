class PatchInfo:
    ID = str
    Name = str
    Versions = []
    
    def __init__(self, _id = str, name = str, versions=None):
        if versions is None:
            versions = []
        self.ID = _id
        self.Name = name
        self.Versions = versions