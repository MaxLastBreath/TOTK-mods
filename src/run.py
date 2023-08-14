import ttkbootstrap as ttk
import threading
from ttkbootstrap.constants import *
from form import Manager
from modules.update import textver, check_for_updates, delete_old_exe

if __name__ == "__main__":
    # Delete any old executables
    delete_old_exe()

    window = ttk.Window(themename="flatly")
    window.title(f"TOTK Optimizer {textver}")
    main = Manager(window)
    window_width = 1200
    window_height = 600
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    window.resizable(False, False)
    check_for_updates()
    window.mainloop()