import ttkbootstrap as ttk
from modules.logger import *
from form import Manager
from modules.update import textver, check_for_updates, delete_old_exe
from modules.scaling import sf, scale
from ctypes import *

if __name__ == "__main__":
    try:
        if platform.system() == "Windows":
            windll.shcore.SetProcessDpiAwareness(2)
            windll.user32.SetProcessDPIAware()


        window = ttk.Window(scaling=sf)
        window.title(f"TOTK Optimizer {textver}")
        main = Manager(window)
        window_width = scale(1200)
        window_height = scale(600)
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        window.minsize(window_width, window_height)
        window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        window.resizable(False, False)
        ttk.Style().configure('TButton', foreground='white', font=('Comic Sans MS', 10, 'bold'))

        # Delete any old executables
        # Disabled for MacOS (For now)
        if platform.os() != "Darwin":
            delete_old_exe()
            check_for_updates()
        window.mainloop()
    except Exception as e:
        log.critical("ERROR AT MAIN: " + e)