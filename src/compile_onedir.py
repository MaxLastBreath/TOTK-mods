import platform
import subprocess
import zipfile
import os
from configuration.settings import *

latest_version = Version.strip("manager-")

def create_zip(source_dir, dest_file):
    with zipfile.ZipFile(dest_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_dir)
                zip_path = os.path.join('TOTK Optimizer', relative_path)
                zipf.write(file_path, zip_path)

if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "pyinstaller",
            "run.py",
            "--onedir",
            f"--name=TOTK Optimizer {latest_version}",
            "--add-data", "GUI;GUI",
            "--add-data", "json.data;json.data",
            "--icon", "GUI/LOGO.ico"
        ]
        subprocess.run(command, shell=True)
        create_zip(f'dist/TOTK Optimizer {latest_version}', f'dist/TOTK_Optimizer_{latest_version}_Windows.zip')
    elif platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onedir",
            f"--name=TOTK Optimizer {latest_version}",
            "run.py",
            "--add-data", "GUI:GUI",
            "--add-data", "json.data:json.data",
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap"
        ]
        subprocess.run(command, check=True)
        create_zip(f'dist/TOTK Optimizer {latest_version}', f'dist/TOTK_Optimizer_{latest_version}_Linux.zip')