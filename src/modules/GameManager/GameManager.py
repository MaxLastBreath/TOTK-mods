from modules.GameManager.PatchInfo import PatchInfo
import json
import os

class Game_Manager:
    GamePatches = []

    def __init__(self):
        self.LoadPatches()

    @classmethod
    def LoadPatches(cls):
        current_directory = os.path.curdir
        patch_directory =  os.path.join(current_directory, "Patches")

        if not os.path.exists(patch_directory):
           raise "NO PATCHES FOUND, Please check your installation"
        
        print(patch_directory)
        
        for folder in os.listdir(patch_directory):
            patchfolder = os.path.join(patch_directory, folder)

            for gamefolder in os.listdir(patchfolder):
                filepath =  os.path.join(patchfolder, gamefolder)

                if (gamefolder == "PatchInfo.json"):
                    with open(filepath, "r", encoding="utf-8") as file:
                        jsonfile = json.load(file)
                    print(f"{jsonfile['ID']}, {jsonfile['Name']}, {jsonfile['Versions']}")

                    cls.GamePatches.append(
                            PatchInfo(
                                patchfolder,
                                jsonfile["ID"], 
                                jsonfile["Name"], 
                                jsonfile["Versions"],
                                jsonfile["ModName"],
                                jsonfile["ModConfig"]
                                      )
                        )
                        
    @classmethod
    def GetPatches(cls):
        if not cls.GamePatches:
            cls.LoadPatches()
        return cls.GamePatches
    
    @classmethod
    def FindCurrentPatch(clss):
        print("Does Nothing")