import requests
import os
import shutil
from packaging.version import Version, parse
import platform
import sys
import glob
import subprocess
import tkinter as tk
from tkinter import messagebox

Version = "manager-1.2.0"
textver = Version.strip("manager-")
GITHUB = "TOTK-mods"
OWNER = "MaxLastBreath"
def show_confirmation_dialog(remote_version_str):
    result = messagebox.askyesno("Confirmation", f"Mod Manager version {remote_version_str} was found, do you want to apply the update?")
    return result

# Check For Update
def check_for_updates():
    print("Checking for Updates!")
    url = f"https://api.github.com/repos/{OWNER}/{GITHUB}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        response.raise_for_status()
        release_info = response.json()
        remote_version_str = release_info["tag_name"].strip("manager-")
        remote_version = parse(remote_version_str)

        if remote_version > parse(textver):
            confirmation_result = show_confirmation_dialog(remote_version_str)
            if confirmation_result:
               download_update(release_info["assets"])
            else:
                return
        else:
            print("No Updates Found. Your app is up to date.")

def download_update(assets):
    current_platform = platform.system()

    for asset in assets:
        asset_name = asset["name"]
        asset_url = asset["browser_download_url"]
        
        if current_platform == "Linux" and asset_name.endswith(".AppImage"):
            print(f"Downloading {asset_name}")
            try:
                response = requests.get(asset_url)
                response.raise_for_status()
            except requests.RequestException as e:
                print("Error downloading asset:", e)
                return

            with open(asset_name, "wb") as f:
                f.write(response.content)

            print("Asset downloaded successfully.")

        elif current_platform == "Windows" and asset_name.endswith(".exe"):
            print(f"Downloading {asset_name}")
            try:
                response = requests.get(asset_url)
                response.raise_for_status()
            except requests.RequestException as e:
                print("Error downloading asset:", e)
                return

            with open(asset_name, "wb") as f:
                f.write(response.content)

            print("Asset downloaded successfully.")
        apply_update(assets)

def apply_update(assets):
    print("Applying Update...")
    current_platform = platform.system()
    updated_executable = None

    for asset in assets:
        asset_name = asset["name"]
        if current_platform == "Windows" and asset_name.endswith(".exe"):
            updated_executable = asset_name
            break

    if updated_executable is None:
        print("No Windows executable found in the assets.")
        return

    try:
        old_executable = sys.argv[0]
        if os.path.exists(old_executable):
            os.rename(old_executable, f"{old_executable}.tmp")
            print("Old executable deleted.")

        if sys.platform.startswith("linux"):
            os.chmod(updated_executable, 0o755)
        elif sys.platform.startswith("win"):
            pass 

        os.execl(updated_executable, *([updated_executable] + sys.argv[1:]))
    except Exception as e:
        print(f"Error applying update: {e}")
        return

    print("Update Applied. Exiting...")
    sys.exit()

def delete_old_exe():
    executable_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    current_platform = platform.system()
    try:
        # Remove old versions of manager
        matching_files = glob.glob(os.path.join(executable_directory, "*.exe.tmp"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.3.exe"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.2.exe"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.1.exe"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.0.exe"))
        matching_files += glob.glob(os.path.join(executable_directory, "*appimage.tmp"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.3.appimage.tmp"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.2.appimage.tmp"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.1.appimage.tmp"))
        matching_files += glob.glob(os.path.join(executable_directory, "*1.1.0.appimage.tmp"))

        for file_path in matching_files:
            print("Removing old exe:", file_path)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    except Exception as e:
        print("Error:", e)