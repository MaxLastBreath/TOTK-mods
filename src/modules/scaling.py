import platform
import configparser
from ctypes import *
from screeninfo import *

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
        sf = 2.0
        return sf
    if w_scale == "On":
        h = 1080
        if platform.system() == "Windows":
            windll.shcore.SetProcessDpiAwareness(1)
        try:
            monitors = get_monitors()
            for monitor in monitors:
                if monitor.is_primary:
                    h = monitor.height
        except Exception as e:
            return 1.0
        if h <= 1080 and h < 1440:
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

