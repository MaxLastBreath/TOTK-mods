import tkinter as ttk
import ctypes
import platform
if platform.system() == "Windows":
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

def scalingfactor(baseline_resolution=(1920, 1080)):
    window = ttk.Tk()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    window.destroy()

    baseline_width, baseline_height = baseline_resolution


    scaling_factor_width = screen_width // baseline_width
    scaling_factor_height = screen_height // baseline_height
    print(f"{screen_width}, {baseline_width}")

    scaling_factor = min(scaling_factor_width, scaling_factor_height)
    print(f"Scaling Factor: {scaling_factor}")
    return scaling_factor
