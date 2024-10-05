class PatchInfo:
    Folder = "Patches/Tears Of The Kingdom"
    Name = "Tears of The Kingdom"
    ID = "0100F2C0115B6000"
    ModName = "!!!TOTK Optimizer"
    Config = "UltraCam/maxlastbreath.ini"
    Versions = []
    
    def __init__(self, folder = str, _id = str, name = str, versions=None, modName = str, configloc = str):
        if versions is None:
            versions = []
        self.Folder = folder
        self.ID = _id
        self.Name = name
        self.Versions = versions
        self.ModName = modName
        self.Config = configloc

    def LoadJson(self):
        print()