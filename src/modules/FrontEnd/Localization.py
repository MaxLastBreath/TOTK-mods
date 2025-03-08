import json, os
from run_config import __ROOT__


class Localization:

    Folder: str = "Localization"

    @classmethod
    def GetJson(cls) -> json:

        location = os.path.join(os.path.curdir, cls.Folder)

        if not os.path.exists(location):
            location = os.path.join(__ROOT__, cls.Folder)

        JsonFile = os.path.join(location, "en.json")
        with open(JsonFile, "r", encoding="utf-8") as file:
            return json.load(file)
