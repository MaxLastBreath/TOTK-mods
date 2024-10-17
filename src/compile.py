import platform
import subprocess
import os
from configuration.settings import *

latest_version = Version.strip("manager-")
program_name = "NX Optimizer"

if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "pyinstaller",
            "run.py",
            "--onefile",
            f"--name={program_name} {latest_version}",
            "--add-data",
            "GUI;GUI",
            "--add-data",
            "Localization;Localization",
            "--add-data",
            "PatchInfo;PatchInfo",
            "--icon",
            "GUI/LOGO.ico",
        ]
        subprocess.run(command, shell=True)

    elif platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onefile",
            f"--name={program_name} {latest_version}.AppImage",
            "run.py",
            "--add-data",
            "GUI:GUI",
            "--add-data",
            "Localization:Localization",
            "--add-data",
            "PatchInfo:PatchInfo" "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)

    elif platform.system() == "Darwin":
        command = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--noconfirm",
            f"--name={program_name}",
            "run.py",
            "--add-data",
            "Localization:Localization",
            "--add-data",
            "GUI:GUI",
            "--add-data",
            "PatchInfo:PatchInfo",
            "--icon",
            "GUI/LOGO.icns",
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)
        if os.path.exists(f"dist/{program_name}"):
            os.remove(f"dist/{program_name}")
