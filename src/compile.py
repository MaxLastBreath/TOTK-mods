import platform
import subprocess
from distutils.core import setup
import py2exe
from configuration.settings import *
latest_version = Version.strip("manager-")


if __name__ == "__main__":
    if platform.system() == "Windows":
        setup(
            console=[
                {
                    "script": "run.py",
                    "dest_base": f"TOTK_Optimizer_{latest_version}",
                }
            ],
            options={
                "py2exe": {
                    "bundle_files": 1,
                    "dll_excludes": ["MSVCP90.dll"],
                    "optimize": 2,
                }
            }
        )

        subprocess.run("python setup.py py2exe", shell=True)
        
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
