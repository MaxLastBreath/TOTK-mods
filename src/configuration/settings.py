from modules.colors import Color
from modules.scaling import scale, sf
from modules.json import load_json
import configparser

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
btnfont = ("Arial", 10)
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
