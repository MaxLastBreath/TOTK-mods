import platform
import subprocess
import os
from configuration.settings import *

latest_version = Version.strip("manager-")

if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "pyinstaller",
            "run.py",
            "--onefile",
            f"--name=NX Optimizer {latest_version}",
            "--add-data",
            "GUI;GUI",
            "--add-data",
            "json.data;json.data",
            "--icon",
            "GUI/LOGO.ico",
        ]
        subprocess.run(command, shell=True)

    elif platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onefile",
            f"--name=NX Optimizer {latest_version}.AppImage",
            "run.py",
            "--add-data",
            "GUI:GUI",
            "--add-data",
            "json.data:json.data" "--hidden-import=PIL",
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
            f"--name=NX Optimizer",
            "run.py",
            "--add-data",
            "GUI:GUI",
            "--add-data",
            "json.data:json.data",
            "--icon",
            "GUI/LOGO.icns",
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)
        if os.path.exists("dist/NX Optimizer"):
            os.remove("dist/NX Optimizer")
