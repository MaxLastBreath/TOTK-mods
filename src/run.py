import tkinter as tk
from tkinter import CURRENT, ttk
from form import Manager

currentver = "1.0.3"
# Create the main window
if __name__ == "__main__":
    window = tk.Tk()
    window.title(f"TOTK MOD Manager {currentver}")
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
