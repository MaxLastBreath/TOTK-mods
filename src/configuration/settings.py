from modules.colors import Color
from modules.scaling import scalingfactor

sf = int(scalingfactor())
if sf == 0:
    sf = 1
fs = 10
if sf > 1:
    fs = 9


html_color = Color()
# Settings for the manager.
Hoverdelay = 500
title_id = "72324500776771584"
localconfig = "Manager_Config.ini"
font = "Arial Bold"
textfont = (font, fs)
bigfont = ("Triforce", 15)
textcolor = html_color["light-cyan"]
BigTextcolor = html_color["light-green"]
outlinecolor = html_color["purple"]
style = "danger"

# URLS
dfpsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/DFPS.json"
cheatsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Cheats.json"
presetsurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/presets.json"
versionurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/VersionNew.json"
descurl = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Description.json"