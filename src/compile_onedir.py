import platform
import subprocess
import zipfile
import os
from configuration.settings import *
import argparse

latest_version = Version.strip("manager-")

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--os')
args = parser.parse_args()

def create_zip(source_dir, dest_file):
    with zipfile.ZipFile(dest_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_dir)
                zip_path = os.path.join('TOTK Optimizer', relative_path)
                zipf.write(file_path, zip_path)

def delete_directory(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    os.rmdir(folder)

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
    elif args.os == "MacOS-Intel":
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
        if os.path.exists("dist/TOTK Optimizer"): delete_directory("dist/TOTK Optimizer")

        os.mkdir('dist/archive')
        os.rename('dist/TOTK Optimizer.app', 'dist/archive/TOTK Optimizer.app')
        create_zip('dist/archive', f'dist/TOTK_Optimizer_{latest_version}_MacOS_Intel.zip')

    elif args.os == "MacOS-Silicon":
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
        if os.path.exists("dist/TOTK Optimizer"): delete_directory("dist/TOTK Optimizer")

        os.mkdir('dist/archive')
        os.rename('dist/TOTK Optimizer.app', 'dist/archive/TOTK Optimizer.app')
        create_zip('dist/archive', f'dist/TOTK_Optimizer_{latest_version}_MacOS_Silicon.zip')

    # Remove unnecessary files
    if os.path.exists("dist/TOTK Optimizer"): delete_directory("dist/TOTK Optimizer")
    if os.path.exists("dist/archive"): delete_directory("dist/archive")