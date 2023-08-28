import configparser
import os
import shutil
import sys
import time

import requests
import json
from packaging.version import parse
from modules.download import get_zip_list_and_dict

localconfig = "Manager_Config.ini"


def load_json(name, url):
    # Check if the .presets folder exists, if not, create it
    presets_folder = "json.data"
    if not os.path.exists(presets_folder):
        os.makedirs(presets_folder)
    json_url = url
    json_options_file_path = os.path.join(presets_folder, name)

    try:
        response = requests.get(json_url, timeout=5)
        response.raise_for_status()

        data = response.json()

        if os.path.exists(json_options_file_path):
            with open(json_options_file_path, "r") as file:
                local_json_options = json.load(file)

            if data != local_json_options:
                with open(json_options_file_path, "w") as file:
                    json.dump(data, file, indent=4)
                    json_options = data
            else:
                json_options = local_json_options
        else:
            with open(json_options_file_path, "w") as file:
                json.dump(data, file, indent=4)
                json_options = data

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error occurred while fetching or parsing Description.json: {e}")
        if os.path.exists(json_options_file_path):
            with open(json_options_file_path, "r") as file:
                json_options = json.load(file)
            # Fetch stored json data.
        else:
            json_options_file_path = fetch_local_json(name)
            with open(json_options_file_path, "r") as file:
                json_options = json.load(file)

    return json_options


time_config = configparser.ConfigParser()
time_config.read(localconfig)

old_time = float(time_config.get("Time", "api", fallback=0))


# Pull new links only once an hour. - Avoids overwhelming Github API.
def fetch_local_json(name):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)

    return os.path.join(base_path, f'json.data/{name}')

def load_values_from_json():
    global AR_list, AR_dict, UI_list, UI_dict, FP_list, FP_dict, DFPS_list, DFPS_dict

    json_file_path = 'json.data/api.json'
    try:
        with open(json_file_path, "r") as json_file:
            api_json = json.load(json_file)
    except Exception as e:
        json_file_path = fetch_local_json("api.json")
        with open(json_file_path, "r") as json_file:
            api_json = json.load(json_file)

    AR_list = api_json["AR_list"]
    AR_dict = api_json["AR_dict"]
    UI_list = api_json["UI_list"]
    UI_dict = api_json["UI_dict"]
    FP_list = api_json["FP_list"]
    FP_dict = api_json["FP_dict"]
    DFPS_list = api_json["DFPS_list"]
    DFPS_dict = api_json["DFPS_dict"]


try:
    if time.time() - old_time >= 3600 or not os.path.exists("json.data/api.json"):
        skip = ["XBOX", "UI", "PS4", "STEAMDECK"]
        AR = get_zip_list_and_dict(
            "https://api.github.com/repos/MaxLastBreath/TOTK-mods/contents/scripts/Mods/Aspect%20Ratios", skip=skip)
        AR_list = AR[0]
        AR_list.insert(0, "Aspect Ratio 16-9")
        AR_dict = AR[1]

        UI = get_zip_list_and_dict(
            "https://api.github.com/repos/MaxLastBreath/TOTK-mods/contents/scripts/Mods/UI%20Mods")
        UI_list = UI[0]
        UI_list.insert(0, "None")
        UI_dict = UI[1]

        FP = get_zip_list_and_dict(
            "https://api.github.com/repos/MaxLastBreath/TOTK-mods/contents/scripts/Mods/FP%20Mods")
        FP_list = FP[0]
        FP_list.insert(0, "Off")
        FP_dict = FP[1]

        DFPS = get_zip_list_and_dict("https://api.github.com/repos/MaxLastBreath/TOTK-mods/contents/scripts/Mods/DFPS")
        DFPS_list = DFPS[0]
        DFPS_list.reverse()
        DFPS_dict = DFPS[1]

        latest = "1.0.0"
        cur_beta = 0
        # Push the Latest available version link.
        for item in DFPS_list:
            if item == "Latest": continue
            vers = item.split(" ")[1]
            if item.endswith(")"):
                beta1 = item.split("(Beta")[1]
                beta = beta1.split(")")[0]
            else:
                beta = 0

            if parse(latest) < parse(vers):
                latest = vers
                full_latest = item
            if parse(latest) == parse(vers):
                if int(cur_beta) < int(beta):
                    full_latest = item

        DFPS_list.insert(0, "Latest")
        DFPS_dict["Latest"] = DFPS_dict.get(full_latest)

        api_json = {
            "AR_list": AR_list,
            "AR_dict": AR_dict,
            "UI_list": UI_list,
            "UI_dict": UI_dict,
            "FP_list": FP_list,
            "FP_dict": FP_dict,
            "DFPS_list": DFPS_list,
            "DFPS_dict": DFPS_dict
        }
        if not os.path.exists("json.data"):
            os.makedirs("json.data")
        try:
            with open("json.data/api.json", "w") as json_file:
                json.dump(api_json, json_file, indent=4)
        except PermissionError as e:
            shutil.rmtree("json.data/api.json")
        # Save Time.
        if not time_config.has_section("Time"):
            time_config["Time"] = {}

        time_config["Time"]["api"] = f"{time.time()}"
        with open(localconfig, 'w') as file:
            time_config.write(file)
    else:
        load_values_from_json()
except requests.exceptions.ConnectionError as e:
    load_values_from_json()
except TypeError as e:
    load_values_from_json()