import platform
import subprocess
from configuration.settings import *
from cx_Freeze import setup, Executable
latest_version = Version.strip("manager-")


if __name__ == "__main__":
    if platform.system() == "Windows":
        base = "Win32GUI"
        options = {
            "build_exe": {
                "packages": [],
                "include_files": [
                    ("GUI", "GUI"),
                    ("json.data", "json.data")
                ]
            }
        }

        executables = [
            Executable("run.py", base=base, targetName=f"TOTK_Optimizer_{latest_version}.exe")
        ]

        setup(
            name="TOTK_Optimizer",
            options=options,
            version=latest_version,
            description="Your application description",
            executables=executables
)
        
    if platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onefile",
            "--collect-all", "ttkbootstrap",
            f"--name=TOTK Optimizer {latest_version}.AppImage",
            "run.py",
            "--add-data", "GUI:GUI",
            "--add-data", "json.data:json.data"
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)
