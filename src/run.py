import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from form import Manager
from modules.update import textver, check_for_updates

if __name__ == "__main__":
    check_for_updates()
    window = ttk.Window(themename="flatly")
    window.title(f"TOTK MOD Manager {textver}")
    main = Manager(window)
    window_width = 1200
    window_height = 600
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    reference_resolution = 1920
    scaling_factor = screen_width / reference_resolution
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    window.resizable(False, False)
    window.mainloop()