from modules.logger import log, superlog
import json, os, sys


class PatchInfo:
    Folder: str = "PatchInfo/Tears Of The Kingdom"
    Name: str = "Tears of The Kingdom"
    ID: str = "0100F2C0115B6000"
    ModName: str = "!!!TOTK Optimizer"
    Config: str = "UltraCam/maxlastbreath.ini"
    ModFolder: str = ""
    Versions: list[str] = []
    Cheats: bool = False
    ResolutionScale: bool = True

    def __init__(self, folder: str, JsonFile: json):  # fmt: skip
        
        self.Folder = folder
        self.ID = self.Json(JsonFile, "ID") # mandatory
        self.Name = self.Json(JsonFile, "Name") # mandatory
        self.Versions = self.Json(JsonFile, "Versions", [])
        self.ModName = self.Json(JsonFile, "ModName", "!!!NX-Optimizer")
        self.Config = self.Json(JsonFile, "ModConfig")
        self.ModFolder = self.Json(JsonFile, "ModFolder")
        self.Cheats = self.Json(JsonFile, "Cheats", False)
        self.SDCardConfig = self.Json(JsonFile, "SDCardConfig", False)
        self.ResolutionScale = self.Json(JsonFile, "EmulationScale", True)

    def Json(self, JsonFile, Entry, fallback=None):
        try:
            ReturnValue = JsonFile[Entry]
        except KeyError:
            log.error(f"Couldn't fetch {Entry} for {self.Json(JsonFile, 'Name', fallback='ERROR')}")
            return fallback
        return ReturnValue
        
    def GetModPath(self) -> str:
        location = os.path.join(self.Folder, self.ModFolder)
        return location

    def IDtoNum(self):
        return int(self.ID, 16)

    def LoadJson(self):
        Location = os.path.join(self.Folder, "Options.json")
        with open(Location, "r", encoding="utf-8") as file:
            return json.load(file)

    def LoadPresetsJson(self):
        Location = os.path.join(self.Folder, "Presets.json")

        if not os.path.exists(Location):
            return {"Saved": {}}

        with open(Location, "r", encoding="utf-8") as file:
            return {"Saved": {}} | json.load(file)

    def LoadCheatsJson(self):
        if self.Cheats is False:
            log.warning("No Cheats detected")
            return
        if self.Cheats is True:
            Location = os.path.join(self.Folder, "Cheats.json")
            with open(Location, "r", encoding="utf-8") as file:
                return json.load(file)
