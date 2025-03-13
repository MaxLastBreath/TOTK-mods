from tkinterdnd2 import DND_FILES
import ttkbootstrap as ttk
from modules.logger import *
from modules.GameManager.GameManager import Game_Manager, PatchInfo
import zipfile
import os
import re

class DragFile:
    _manager = None

    def process_file(self, zip_path):
        os.makedirs(Game_Manager._Directory, exist_ok=True)
        patchInfo: PatchInfo = None
        patchnames:list[str] = []

        with zipfile.ZipFile(zip_path, 'r') as ref:
            ref.extractall(Game_Manager._Directory)
            patchnames = ref.namelist()
            patchnames = [file for file in patchnames if file.count('/') == 1]
            log.info(patchnames)

        for patch in patchnames:
            patchdir = os.path.normpath(os.path.join(Game_Manager._Directory, patch))
            if os.path.exists(patchdir) and os.path.isdir(patchdir):
                log.info(f"Creating Patch Info {patchdir}")
                patchInfo = Game_Manager.CreatePatchInfo(patchdir)

                if (patchInfo is not None):
                    self._manager.SetPatch(patchInfo)
                    self._manager.LoadNewGameInfo()

    def load_files(self, event):
        file_path: str = ""
        files = re.findall(r'\{.*?\}|\S+', event.data.strip())
        files = [file[1:-1] if file.startswith('{') and file.endswith('}') else file for file in files]
        for file_path in files:
            if (file_path.endswith(".nxop")): #NX-Optimizer Patch.
                log.info(f"Processing NX Optimizer Patch File {file_path}")
                self.process_file(file_path)
            else:
                log.error(f"File {file_path} isn't a Patch File .nxop")

    def __init__(self, window: ttk.Window, MGR):
        from modules.FrontEnd.FrontEnd import Manager
        self._manager: Manager = MGR

        window.drop_target_register(DND_FILES)
        window.dnd_bind('<<Drop>>', self.load_files)