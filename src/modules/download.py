from inspect import Traceback
from socket import socket
from urllib.error import URLError
import requests
import urllib.request
import os
import zipfile
from io import BytesIO


class Download:
    def __init__(self):
        self.download = ""


def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
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
        response = urllib.request.urlopen(url)
        zip_content = BytesIO(response.read())
        # Create a ZipFile object
        with zipfile.ZipFile(zip_content, 'r') as zip_ref:
            # Extract all contents to a target directory
            zip_ref.extractall(target_directory)
    except URLError as e:
        print(
                f"Invalid download URL {url}, possibly due to no internet connection."
                f"Downloading has been halted.")


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
                with open(file_name, 'wb') as file:
                    file.write(file_response.content)
                print(f'copied file: {file_name}')

        elif item['type'] == "dir":
            folder_name = os.path.join(dir, item['name'])
            os.makedirs(folder_name, exist_ok=True)
            sub_folder_contents = item['url']
            print(sub_folder_contents)
            download_folders(sub_folder_contents, folder_name)


def get_option_list(url, skip=[]):
    # accepting only single word list.
    full_list = []
    response = requests.get(url)
    print(response.json())
    if not response.status_code == 200:
        return

    for item in response.json():
        if any(sub_item in item["name"].split(" ") for sub_item in skip):
            continue
        if item['type'] == "dir":
            full_list.append(item["name"])

    return full_list


def get_zip_list_and_dict(url, skip=[]):
    # accepting only single word list.
    full_list = []
    full_dict = {}
    response = requests.get(url)
    if not response.status_code == 200:
        return

    for item in response.json():

        if item['type'] == "file":
            full_dict[item["name"].split(".zip")[0]] = item["download_url"]

        if any(sub_item in item["name"].split(" ") for sub_item in skip):
            continue

        if item['type'] == "file":
            full_list.append(item["name"].split(".zip")[0])
    return full_list, full_dict


def get_api_dict(url):
    # accepting only single word list.
    full_dict = {}
    response = requests.get(url)
    if not response.status_code == 200:
        return

    for item in response.json():
        if item['type'] == "dir":
            full_dict[item["name"]] = item["url"]
    return full_dict

