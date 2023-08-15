from modules.colors import Color
from modules.scaling import scale, sf


fontsize = 13
bigfontsize = 18
CH = 26
FPS = 0.05

# SET animation FPS to lower if higher resolution.
if sf > 1.0:
    FPS = 0.1
    CH +=5
if sf > 1.5:
    CH +=5

CBHEIGHT = CH
html_color = Color()
# Settings for the manager.
Hoverdelay = 500
title_id = "72324500776771584"
localconfig = "Manager_Config.ini"
font = "Arial Bold"
textfont = (font, fontsize)
btnfont = ("Arial Bolds", fontsize - 3)
bigfont = ("Triforce", bigfontsize)
biggyfont = ("Arial Bold", bigfontsize, "bold")
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