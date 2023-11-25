import ttkbootstrap as ttk
from form import Manager
from modules.update import textver, check_for_updates, delete_old_exe
from modules.scaling import sf, scale

if __name__ == "__main__":
    window = ttk.Window(scaling=sf)
    window.title(f"TOTK Optimizer {textver}")
    main = Manager(window)
    window_width = scale(1200)
    window_height = scale(600)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    window.resizable(False, False)
    ttk.Style().configure('TButton', foreground='white', font=('Comic Sans MS', 10, 'bold'))
    # Delete any old executables
    delete_old_exe()
    check_for_updates()
    window.mainloop()