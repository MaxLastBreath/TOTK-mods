from modules.GameManager.PatchInfo import PatchInfo
from modules.logger import log, superlog
import json, os, sys, platform


class Game_Manager:
    GamePatches: list[PatchInfo] = []
    DefaultID: str = "0100F2C0115B6000"
    Directory: str = "PatchInfo"
    PatchFile: str = "PatchInfo.json"

    def __init__(self):
        self.LoadPatches()

    @classmethod
    def LoadPatches(cls) -> None:
        current_directory = os.path.curdir
        patch_directory = os.path.join(current_directory, cls.Directory)

        if not os.path.exists(patch_directory):
            if getattr(sys, "frozen", False):
                patch_directory = os.path.join(sys._MEIPASS, cls.Directory)
                superlog.warning("No Patch Folder, using stored patches.")

        superlog.info("Looking for supported games...")
        cls.CreatePatches(patch_directory)

    @classmethod
    def CreatePatches(cls, patch_directory) -> None:

        "Loads patch info for each game detected in Patch Folder"

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
                        PatchInfo(patchfolder, jsonfile)
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
