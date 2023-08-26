from modules.colors import Color
from modules.scaling import scale, sf
from modules.json import load_json
from modules.download import *
import configparser
import time
import json

Version = "manager-1.3.0"
repo_url_raw = 'https://github.com/MaxLastBreath/TOTK-mods'
repo_url = 'https://api.github.com/repos/MaxLastBreath/TOTK-mods'
localconfig = "Manager_Config.ini"

# Read Config File.
font = ""
theme = ""
tcolor = ""
toutline = ""
tactive = ""
w_scale = ""
is_auto_backup = ""
is_cheat_backup = ""
is_animation = ""


def get_setting(args=None):
    global font, tcolor, theme, toutline, tactive, is_animation, is_cheat_backup, is_auto_backup, w_scale
    config = configparser.ConfigParser()
    config.read(localconfig)
    font = config.get("Settings", "font", fallback="Arial")
    tcolor = config.get("Settings", "color", fallback="light-cyan")
    toutline = config.get("Settings", "shadow_color", fallback="purple")
    tactive = config.get("Settings", "active_color", fallback="red")
    theme = config.get("Settings", "style", fallback="flatly")
    w_scale = config.get("Settings", "scale", fallback="On")
    is_auto_backup = config.get("Settings", "backup", fallback="Off")
    is_cheat_backup = config.get("Settings", "cheat-backup", fallback="Off")
    is_animation = config.get("Settings", "animation", fallback="On")

    if args in ["back", "backup", "auto-backup"]:
        return is_auto_backup
    if args in ["cback", "cheatbackup", "cheat-backup", "cb"]:
        return is_cheat_backup
    if args in ["ani", "animation"]:
        return is_animation


get_setting()
CH = 26
FPS = 0.05

# SET animation FPS to lower if higher resolution.
if sf > 1.0:
    CH +=5

if sf > 1.5:
    FPS = 0.1
    CH +=5

CBHEIGHT = CH
html_color = Color()

# Settings for the manager.
Hoverdelay = 500
title_id = "72324500776771584"

# Set fonts
textfont = (font, 13)
btnfont = ("bahnschrift", 10)
bigfont = ("Triforce", 18)
biggyfont = (font, 18, "bold")
# set Colors
textcolor = html_color[tcolor]
outline_color = html_color[toutline]
active_color = html_color[tactive]
BigTextcolor = html_color["light-green"]


style = "danger"

# URLS
dfpsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/DFPS.json"
cheatsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Cheats.json"
presetsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/presets.json"
versionurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/VersionNew.json"
descurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Description.json"

description = load_json("Description.json", descurl)

time_config = configparser.ConfigParser()
time_config.read(localconfig)


old_time = float(time_config.get("Time", "api", fallback=0))
if time.time() - old_time >= 3600 or not os.path.exists("json.data/api.json"):
    if not time_config.has_section("Time"):
        time_config["Time"] = {}

    time_config["Time"]["api"] = f"{time.time()}"
    with open(localconfig, 'w') as file:
        time_config.write(file)

    skip = ["XBOX", "UI", "PS4", "STEAMDECK"]
    AR = get_zip_list_and_dict("https://api.github.com/repos/MaxLastBreath/TOTK-mods/contents/scripts/Mods/Aspect%20Ratios", skip=skip)
    AR_list = AR[0]
    AR_list.insert(0, "Aspect Ratio 16-9")
    AR_dict = AR[1]

    UI = get_zip_list_and_dict("https://api.github.com/repos/MaxLastBreath/TOTK-mods/contents/scripts/Mods/UI%20Mods")
    UI_list = UI[0]
    UI_list.insert(0, "None")
    UI_dict = UI[1]

    FP = get_zip_list_and_dict("https://api.github.com/repos/MaxLastBreath/TOTK-mods/contents/scripts/Mods/FP%20Mods")
    FP_list = FP[0]
    FP_list.insert(0, "Off")
    FP_dict = FP[1]

    api_json = {
        "AR_list": AR_list,
        "AR_dict": AR_dict,
        "UI_list": UI_list,
        "UI_dict": UI_dict,
        "FP_list": FP_list,
        "FP_dict": FP_dict
    }
    with open("json.data/api.json", "w") as json_file:
        json.dump(api_json, json_file, indent=4)

else:
    with open("json.data/api.json", "r") as json_file:
        api_json = json.load(json_file)
    AR_list = api_json["AR_list"]
    AR_dict = api_json["AR_dict"]
    UI_list = api_json["UI_list"]
    UI_dict = api_json["UI_dict"]
    FP_list = api_json["FP_list"]
    FP_dict = api_json["FP_dict"]
