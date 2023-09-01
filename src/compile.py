import platform
import subprocess
from configuration.settings import *
latest_version = Version.strip("manager-")


if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "nuitka",
            "--recurse-all",
            "--standalone",
            "--output-dir=dist",
            "--output-name=TOTK_Optimizer_" + latest_version + ".exe",
            "run.py"
        ]
        
        subprocess.run(command, shell=True)
        
    if platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onefile",
            "--collect-all", "ttkbootstrap",
            "run.py",
            f"--name=TOTK Optimizer {latest_version}.AppImage",
            "--add-data", "GUI:GUI",
            "--add-data", "json.data:json.data"
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)
