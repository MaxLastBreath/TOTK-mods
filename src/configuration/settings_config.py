import ttkbootstrap as ttk
from modules.scaling import scale, sf
from configuration.settings import textfont, textcolor

def settingswindow(mode, event=None):
    if mode.lower() == "Create" or "c":
        canvas()

def canvas():
    window = createwindow()
    canvas = ttk.Canvas(window, width = scale(400), height=scale(400), bg="black")
    canvas.pack()

    row = scale(40)
    cultex = scale(40)
    culsel = scale(180)

    canvas.create_text(cultex, row, text="Disable Animations:", anchor="w", fill=textcolor, font=textfont)
    row += scale(40)

    canvas.create_text(cultex, row, text="Choose Font:", anchor="w", fill=textcolor, font=textfont)
    row += scale(40)

    canvas.create_text(cultex, row, text="Text Color:", anchor="w", fill=textcolor, font=textfont)
    row += scale(40)

    canvas.create_text(cultex, row, text="Choose Style:", anchor="w", fill=textcolor, font=textfont)
    row += scale(40)

    canvas.create_text(cultex, row, text="Scale With Windows:", anchor="w", fill=textcolor, font=textfont)
    row += scale(40)

    canvas.create_text(cultex, row, text="Auto Backup:", anchor="w", fill=textcolor, font=textfont)
    row += scale(40)

    canvas.create_text(cultex, row, text="Auto Backup(Cheats):", anchor="w", fill=textcolor, font=textfont)
    row += scale(40)


def createwindow():
    window = ttk.Window(themename="flatly", scaling=sf)
    window.title(f"Optimizer Settings")
    window_width = scale(400)
    window_height = scale(400)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    window.resizable(False, False)
    return window