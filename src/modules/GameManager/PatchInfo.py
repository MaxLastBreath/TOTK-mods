from modules.logger import log, superlog
import json, os


class PatchInfo:
    Folder: str = "PatchInfo/Tears Of The Kingdom"
    Name: str = "Tears of The Kingdom"
    ID: str = "0100F2C0115B6000"
    ModName: str = "!!!TOTK Optimizer"
    Config: str = "UltraCam/maxlastbreath.ini"
    ModFolder: str = ""
    Versions: list[str] = []
    Cheats: bool = False

    def __init__(self, folder: str, _id: str, name: str, versions: list[str] | None, modName: str, configloc: str, modfolder: str, Cheats: bool):  # fmt: skip
        if versions is None:
            versions = []
        self.Folder = folder
        self.ID = _id
        self.Name = name
        self.Versions = versions
        self.ModName = modName
        self.Config = configloc
        self.ModFolder = modfolder
        self.Cheats = Cheats

    def IDtoNum(self):
        return int(self.ID, 16)

    def LoadJson(self):
        Location = os.path.join(self.Folder, "Options.json")
        with open(Location, "r", encoding="utf-8") as file:
            return json.load(file)

    def LoadCheatsJson(self):
        if self.Cheats is False:
            log.warning("No Cheats detected")
            return
        if self.Cheats is True:
            Location = os.path.join(self.Folder, "Cheats.json")
            with open(Location, "r", encoding="utf-8") as file:
                return json.load(file)
