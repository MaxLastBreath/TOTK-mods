import json, os, sys


class Localization:

    Folder: str = "Localization"

    @classmethod
    def GetJson(cls) -> json:

        location = os.path.join(os.path.curdir, cls.Folder)

        if not os.path.exists(location):
            if getattr(sys, "frozen", False):
                location = os.path.join(sys._MEIPASS, cls.Folder)

        JsonFile = os.path.join(location, "en.json")
        with open(JsonFile, "r", encoding="utf-8") as file:
            return json.load(file)
