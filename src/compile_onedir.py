import zipfile, subprocess, platform
import os, shutil, argparse
from configuration.settings import *

latest_version = Version.strip("manager-")
program_name = "NX Optimizer"

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--os")
args = parser.parse_args()


def create_zip(source_dir, dest_file):
    with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_dir)
                zip_path = os.path.join(program_name, relative_path)
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
            print("Failed to delete %s. Reason: %s" % (file_path, e))
    os.rmdir(folder)


if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "pyinstaller",
            "run.py",
            "--onedir",
            "--clean",
            "--log-level=WARN",
            f"--name={program_name} {latest_version}",
            "--add-data",
            "Localization;Localization",
            "--add-data",
            "GUI;GUI",
            "--add-data",
            "PatchInfo;PatchInfo",
            "--icon",
            "GUI/LOGO.ico",
        ]
        subprocess.run(command, shell=True)
        create_zip(
            f"dist/{program_name} {latest_version}",
            f"dist/{program_name.replace(' ', '_')}_{latest_version}_Windows.zip",
        )

    elif platform.system() == "Linux":
        command = [
            "pyinstaller",
            "--onedir",
            f"--name={program_name} {latest_version}",
            "run.py",
            "--add-data",
            "Localization:Localization",
            "--add-data",
            "GUI:GUI",
            "--add-data",
            "PatchInfo:PatchInfo",
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--hidden-import=PIL._tkinter",
            "--hidden-import=ttkbootstrap",
        ]
        subprocess.run(command, check=True)
        create_zip(
            f"dist/{program_name} {latest_version}",
            f"dist/{program_name.replace(' ', '_')}_{latest_version}_Linux.zip",
        )

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

        processor = "Silicon"
        if platform.processor() == "i386":
            processor = "Intel"

        os.mkdir("dist/archive")
        os.rename(f"dist/{program_name}.app", f"dist/archive/{program_name}.app")
        create_zip(
            "dist/archive",
            f"dist/{program_name.replace(' ', '_')}_{latest_version}_MacOS_{processor}.zip",
        )

    # Remove unnecessary files
    if os.path.exists(f"dist/{program_name}"):
        if os.path.isdir(f"dist/{program_name}"):
            delete_directory(f"dist/{program_name}")
        else:
            os.remove(f"dist/{program_name}")

    if os.path.exists(f"dist/{program_name} {latest_version}"):
        delete_directory(f"dist/{program_name} {latest_version}")
    if os.path.exists("dist/archive"):
        delete_directory("dist/archive")
