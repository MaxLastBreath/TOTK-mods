from tkinterdnd2 import DND_FILES, TkinterDnD
import ttkbootstrap as ttk
from modules.logger import *
from modules.GameManager.GameManager import Game_Manager
import zipfile
import os
import re

class DragFile:

    def process_file(self, zip_path):
        os.makedirs(Game_Manager._Directory, exist_ok=True)

        patchnames:list[str] = []

        with zipfile.ZipFile(zip_path, 'r') as ref:
            ref.extractall(Game_Manager._Directory)
            patchnames = [file for file in ref.namelist() if file.count('/') == 0]

        for patch in patchnames:
            patchdir = os.path.join(Game_Manager._Directory, patch)
            if os.path.exists(patchdir):
                Game_Manager.CreatePatchInfo(patchdir)

    def ondrop(self, event):
        file_path: str = ""
        files = re.findall(r'\{.*?\}|\S+', event.data.strip())
        files = [file[1:-1] if file.startswith('{') and file.endswith('}') else file for file in files]
        for file_path in files:
            if (file_path.endswith(".nxop")): #NX-Optimizer Patch.
                self.process_file(file_path)
                log.info(f"Processing NX Optimizer Patch File {file_path}")
            else:
                log.error(f"File {file_path} isn't a Patch File .nxop")

    def __init__(self, window: ttk.Window):
        window.drop_target_register(DND_FILES)
        window.dnd_bind('<<Drop>>', self.ondrop)