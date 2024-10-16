import json, os


class PatchInfo:
    Folder: str = "Patches/Tears Of The Kingdom"
    Name: str = "Tears of The Kingdom"
    ID: str = "0100F2C0115B6000"
    ModName: str = "!!!TOTK Optimizer"
    Config: str = "UltraCam/maxlastbreath.ini"
    ModFolder: str = ""
    Versions: list[str] = []

    def __init__(self, folder = str, _id = str, name = str, versions=None, modName = str, configloc = str, modfolder = str):  # fmt: skip
        if versions is None:
            versions = []
        self.Folder = folder
        self.ID = _id
        self.Name = name
        self.Versions = versions
        self.ModName = modName
        self.Config = configloc
        self.ModFolder = modfolder

    def IDtoNum(self):
        return int(self.ID, 16)

    def LoadJson(self):
        Location = os.path.join(self.Folder, "Options.json")
        with open(Location, "r", encoding="utf-8") as file:
            return json.load(file)
