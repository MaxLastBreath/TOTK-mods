import platform
import configparser
from screeninfo import get_monitors
from ctypes import *

localconfig = "Manager_Config.ini"

config = configparser.ConfigParser()
config.read(localconfig)
w_scale = config.get("Settings", "scale", fallback="On")

def Auto_SF():
    sf = 1.0
    if w_scale == "1.0x":
        sf = 1.0
    if w_scale == "1.5x":
        sf = 1.5
    if w_scale == "2.0x":
        sf = 1.75
        return sf
    if w_scale == "On":
        if platform.system() == "Windows":
            windll.shcore.SetProcessDpiAwareness(1)
        else:
            # Scale based on the first detected Monitor - For Other OS.
            monitors = get_monitors()
            current_monitor = monitors[0]
            h = current_monitor.height
            print(h)
            if h >= 1080:
                sf = 1.0
            if h >= 1440:
                sf = 1.5
            if h >= 2160:
                sf = 2.0
    return sf

# Use First Monitor to determine SF, this bypasses scaling from windows.
sf = Auto_SF()

def scale(scale):
    if sf == 1.0:
        return scale
    true_vr = float(scale * sf)
    return int(true_vr)

