import tkinter as ttk
import ctypes
import platform
from screeninfo import get_monitors

def Auto_SF():
    if platform.system() == "Windows":
        monitors = get_monitors()
        current_monitor = monitors[0]
        h = current_monitor.height
        print(h)
        sf = 1.0

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
    truevr = float(scale * sf)
    return int(truevr)
        
