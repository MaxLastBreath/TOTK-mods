from modules.GameManager.PatchInfo import PatchInfo
from modules.logger import log, superlog
import json
import os


class Game_Manager:
    GamePatches: list[PatchInfo] = []
    DefaultID: str = "0100F2C0115B6001"
    Directory: str = "Patches"
    PatchFile: str = "PatchInfo.json"

    def __init__(self):
        self.LoadPatches()

    @classmethod
    def LoadPatches(cls) -> None:
        current_directory = os.path.curdir
        patch_directory = os.path.join(current_directory, cls.Directory)

        if not os.path.exists(patch_directory):
            raise "NO PATCHES FOUND, Please confirm your installation is correct."

        superlog.info("Looking for supported games...")

        for folder in os.listdir(patch_directory):
            patchfolder = os.path.join(patch_directory, folder)

            for filename in os.listdir(patchfolder):
                filepath = os.path.join(patchfolder, filename)

                if filename == cls.PatchFile:
                    with open(filepath, "r", encoding="utf-8") as file:
                        jsonfile = json.load(file)
                    log.info(
                        f"{jsonfile['Name']} [{jsonfile['ID']}] : {jsonfile['Versions']}"
                    )

                    cls.GamePatches.append(
                        PatchInfo(
                            patchfolder,
                            jsonfile["ID"],
                            jsonfile["Name"],
                            jsonfile["Versions"],
                            jsonfile["ModName"],
                            jsonfile["ModConfig"],
                            jsonfile["ModFolder"],
                        )
                    )

    @classmethod
    def GetJsonByID(cls, ID: str) -> PatchInfo:
        """Finds the current json file for a TITLEID."""

        for item in cls.GamePatches:
            if ID.lower() == item.ID.lower():
                return item

        # if we don't find anything return TOTK patch.
        for item in cls.GamePatches:
            if item.ID.lower() == cls.DefaultID.lower():
                return item

    @classmethod
    def GetPatches(cls) -> list[PatchInfo]:
        if not cls.GamePatches:
            cls.LoadPatches()
        return cls.GamePatches
