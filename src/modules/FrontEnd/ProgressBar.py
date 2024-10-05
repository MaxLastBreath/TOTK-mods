import ttkbootstrap as ttk
import threading
from modules.logger import *

class ProgressBar:

    string = None
    progress_bar = None
    progress_window = None

    @classmethod
    def Run(cls, window, tasks):
        cls.progress_window = ttk.Toplevel(window)
        cls.progress_window.title("Downloading")
        window_width = 300
        window_height = 100
        screen_width = cls.progress_window.winfo_screenwidth()
        screen_height = cls.progress_window.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        cls.progress_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        cls.progress_window.resizable(False, False)
        total_iterations = 100
        cls.string = ttk.StringVar()
        cls.string.set("Applying the changes.")
        label = ttk.Label(cls.progress_window, textvariable=cls.string)
        label.pack(pady=10)
        cls.progress_bar = ttk.Progressbar(cls.progress_window, mode="determinate", maximum=total_iterations)
        cls.progress_bar.pack(pady=20)
        task_thread = threading.Thread(target=tasks)
        task_thread.start() 
    
    @classmethod
    def Destroy(cls):
        cls.progress_window.destroy()