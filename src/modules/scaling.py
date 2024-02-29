import platform
import configparser
from ctypes import *
from screeninfo import *

CONFIG_FILE_LOCAL_OPTIMIZER = "TOTKOptimizer.ini"

config = configparser.ConfigParser()
config.read(CONFIG_FILE_LOCAL_OPTIMIZER)
w_scale = config.get("Settings", "scale", fallback="On")

def Auto_SF():
    if w_scale == "Off":
        return 1.0
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
    return int(float(scale * sf))

