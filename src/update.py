import requests
import os
import shutil
from packaging.version import Version, parse
import platform
import sys
import subprocess

Version = "manager-1.1.0"
textver = Version.strip("manager-")
GITHUB = "TOTK-mods"
OWNER = "MaxLastBreath"

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
            print("Update Available")
            download_update(release_info["assets"])
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
        apply_update()

def apply_update():
    print("Applying Update...")
    updated_executable = "TOTK Mod Manager"
    try:
        if sys.platform.startswith("linux"):
            subprocess.Popen(["chmod", "+x", updated_executable])
        elif sys.platform.startswith("win"):
            pass 

        subprocess.Popen([updated_executable])
    except Exception as e:
        print(f"Error applying update: {e}")
        return

    print("Update Applied. Exiting...")
    relaunch()

def relaunch():
    sys.exit()