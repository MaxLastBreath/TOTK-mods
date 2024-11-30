from modules.colors import Color
from modules.scaling import *
from modules.json import *
import time
from modules.download import *
import logging
from tkinter import messagebox
import configparser

Version = "manager-2.1.1"
repo_url_raw = 'https://github.com/MaxLastBreath/TOTK-mods'
repo_url = 'https://api.github.com/repos/MaxLastBreath/TOTK-mods'
localconfig = "TOTKOptimizer.ini"

if platform.system() == "Darwin":
    localconfig = os.path.join(macos_path, localconfig)

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

    # Define Fallbacks
    if platform.system() == "Windows":
        fall_font = "Bahnschrift"
        fall_scale = "On"
    else:
        fall_font = "Cascadia"
        fall_scale = "Off"

    config = configparser.ConfigParser()
    config.read(localconfig, encoding="utf-8")
    font = config.get("Settings", "font", fallback=fall_font)
    tcolor = config.get("Settings", "color", fallback="white")
    toutline = config.get("Settings", "shadow_color", fallback="light-orange")
    tactive = config.get("Settings", "active_color", fallback="cyan")
    theme = config.get("Settings", "style", fallback="flatly")
    w_scale = config.get("Settings", "scale", fallback=fall_scale)
    is_auto_backup = config.get("Settings", "backup", fallback="Off")
    is_cheat_backup = config.get("Settings", "cheat-backup", fallback="Off")
    is_animation = config.get("Settings", "animation", fallback="On")
    DFPS_version = config.get("Updates", "dfps", fallback="1.1.0")

    if args in ["back", "backup", "auto-backup"]:
        return is_auto_backup
    if args in ["cback", "cheatbackup", "cheat-backup", "cb"]:
        return is_cheat_backup
    if args in ["ani", "animation"]:
        return is_animation
    if args in ["dfps", "dver"]:
        return DFPS_version
    if args in ["f", "font"]:
        return font


def set_setting(args, value):
    config = configparser.ConfigParser()
    config.read(localconfig, encoding="utf-8")
    if args == "dfps":
        if not config.has_section("Updates"):
            config.add_section("Updates")
        config.set("Updates", "dfps", value)

    with open(localconfig, 'w', encoding="utf-8") as config_file:
        config.write(config_file, space_around_delimiters=False)


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
title_id = "0100F2C0115B6000"
config_title_id = "72324500776771584"

# Set fonts
textfont = (font, 13)
btnfont = ("Bahnschrift", 10)
bigfont = ("Triforce", 18)
biggyfont = (font, 16, "bold")
# set Colors
textcolor = html_color[tcolor]
outline_color = html_color[toutline]
active_color = html_color[tactive]
BigTextcolor = html_color["white"]

style = "danger"

# URLS
cheatsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Cheats.json"
presetsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/beyond_presets.json"
versionurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/VersionNew.json"
descurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Description.json"
Legacy_presets_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Legacy_presets.json"
ultracambeyond = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/UltraCam_Template.json"

# Download UltraCam
New_UCBeyond_Download = f"{repo_url_raw}/raw/main/scripts/Mods/UltraCam/UltraCamBeyond.zip"

# FP download:
FP_Mod = f"{repo_url_raw}/raw/main/scripts/Mods/FP%20Mods/First%20Person.zip"

description = load_json("Description.json", descurl)
