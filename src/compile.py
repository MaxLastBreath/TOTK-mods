import platform
import subprocess
import os
from configuration.settings import *
import argparse

latest_version = Version.strip("manager-")

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version')
args = parser.parse_args()

if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "pyinstaller",
            "run.py",
            "--onefile",
            f"--name=TOTK Optimizer {latest_version}",
            "--add-data", "GUI;GUI",
            "--add-data", "json.data;json.data",
            "--icon", "GUI/LOGO.ico"
        ]
        subprocess.run(command, shell=True)
        
    elif platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onefile",
            f"--name=TOTK Optimizer {latest_version}.AppImage",
            "run.py",
            "--add-data", "GUI:GUI",
            "--add-data", "json.data:json.data"
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap"
        ]
        subprocess.run(command, check=True)
    
    elif args.version == "MacOS x86_64":
        command = [
            "pyinstaller",
            "--target-arch=x86_64",
            "--onedir",
            "--windowed",
            "--noconfirm",
            f"--name=TOTK Optimizer",
            "run.py",
            "--add-data", "GUI:GUI",
            "--add-data", "json.data:json.data",
            "--icon", "GUI/LOGO.icns",
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)
        shutil.rmtree("./dist/TOTK Optimizer")
    
    elif args.version == "MacOS arm64":
        command = [
            "pyinstaller",
            "--target-arch=arm64",
            "--onedir",
            "--windowed",
            "--noconfirm",
            f"--name=TOTK Optimizer",
            "run.py",
            "--add-data", "GUI:GUI",
            "--add-data", "json.data:json.data",
            "--icon", "GUI/LOGO.icns",
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)
        shutil.rmtree("./dist/TOTK Optimizer")
