from modules.logger import *
from urllib.error import URLError
import requests
import certifi
import urllib.request
import os
import zipfile
from tkinter import messagebox
from io import BytesIO


def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb", encoding="utf-8") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded file: {save_path}")
        else:
            print(f"Failed to download file from {url}. Status code: {response.status_code}")
    except requests.exceptions.ConnectionError as e:
            print(
                "No internet connection or api limit reached. Downloading files is halted.")

def download_unzip(url, target_directory):
    try:
        response = urllib.request.urlopen(url, cafile=certifi.where())
        zip_content = BytesIO(response.read())
        # Create a ZipFile object
        with zipfile.ZipFile(zip_content, 'r') as zip_ref:
            # Extract all contents to a target directory
            zip_ref.extractall(target_directory)
    except urllib.error.URLError as e:
        log.error(
                f"Invalid download URL {url}, possibly due to no internet connection."
                f"Downloading has been halted. {e}")
    except zipfile.BadZipFile as e:
        log.error(f"Invalid ZIP file from URL {url}: {e}")
    except Exception as e:
        log.error(f"FAILED TO DOWNLOAD FILE: {url} GOT ERROR: {e}")


def download_folders(api_url, dir):

    response = requests.get(api_url)
    if response.status_code == 200:
        contents = response.json()
        os.makedirs(dir, exist_ok=True)
    else:
        return

    for item in contents:
        if item['type'] == 'file':
            file_url = item.get('download_url')
            file_name = os.path.join(dir, item['name'])

            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                with open(file_name, 'wb', encoding="utf-8") as file:
                    file.write(file_response.content)
                log.info(f'copied file: {file_name}')

        elif item['type'] == "dir":
            folder_name = os.path.join(dir, item['name'])
            os.makedirs(folder_name, exist_ok=True)
            sub_folder_contents = item['url']
            log.info(sub_folder_contents)
            download_folders(sub_folder_contents, folder_name)


def get_zip_list_and_dict(url, skip=[]):
    # accepting only single word list.
    full_list = []
    full_dict = {}
    response = requests.get(url)
    log.info("Attemping to fetch list and dict of zip files.")
    if not response.status_code == 200:
        log.error("Failed to fetch list and dict of zip files. continues...")
        return

    for item in response.json():

        if item['type'] == "file":
            full_dict[item["name"].split(".zip")[0]] = item["download_url"]

        if any(sub_item in item["name"].split(" ") for sub_item in skip):
            continue

        if item['type'] == "file":
            full_list.append(item["name"].split(".zip")[0])
    log.info("Fetch list and dict operation success.")
    return full_list, full_dict
