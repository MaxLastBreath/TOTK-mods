import ttkbootstrap as ttk
import configparser
from modules.scaling import scale, sf
from modules.colors import Color

CH = 26
if sf > 1.0:
    FPS = 0.1
    CH +=5
if sf > 1.5:
    CH +=5

html_color = Color()
textfont = ("Arial", 13)
textcolor = html_color["light-cyan"]
outlinefont = html_color["purple"]
CBHEIGHT = CH
localconfig = "Manager_Config.ini"

class Setting:
    def __init__(self):
        self.window = None
        self.w_scale_var = None
        self.backup_var = None
        self.backup_cheat_var = None
        self.ani_var = None

        self.config = configparser.ConfigParser()
        self.config.read(localconfig)

    def settingswindow(self, style, canvases):
        self.style = style
        self.createwindow()
        self.canvas(canvases)

    def canvas(self, canvases):
        window = self.window
        canvas_obj = ttk.Canvas(master=window, width=scale(400), height=scale(400))

        canvas_obj.pack()

        row = scale(40)
        cultex = scale(40)
        culsel = scale(180)

        # font dropdown menu
        fontlist = ["Arial", "Georgia", "Calibri", "Triforce", "Segoe", "The Wild Breath of Zelda", "Times New Roman", "Tahoma", "Impact", "Lucida"]
        fontlist.sort()
        self.font_var = ttk.StringVar(master=window, value="Arial")
        font = ttk.Combobox(self.window, textvariable=self.font_var, values=fontlist, state="readonly")
        font_window = canvas_obj.create_window(culsel, row, anchor="w", window=font, width=scale(150), height=CBHEIGHT)
        canvas_obj.create_text(cultex, row + 1, text="Choose Font:", anchor="w", fill=outlinefont, font=textfont, tags=["outline"])
        canvas_obj.create_text(cultex, row, text="Choose Font:", anchor="w", fill=textcolor, font=textfont, tags=["text"])
        row += scale(40)

        # color dropdown menu
        colorlist = Color()
        itemlist = colorlist.getlist()
        itemlist.sort()
        self.color_var = ttk.StringVar(master=window, value="light-cyan")
        color = ttk.Combobox(self.window, textvariable=self.color_var, values=itemlist, state="readonly")
        color_window =canvas_obj.create_window(culsel, row, anchor="w", window=color, width=scale(150), height=CBHEIGHT)
        canvas_obj.create_text(cultex, row + 1, text="Text Color:", anchor="w", fill=outlinefont, font=textfont, tags=["outline"])
        canvas_obj.create_text(cultex, row, text="Text Color:", anchor="w", fill=textcolor, font=textfont, tags=["text"])
        row += scale(40)

        # style dropdown menu
        stylelist = self.style.theme_names()
        self.style_var = ttk.StringVar(master=window, value="flatly")
        style = ttk.Combobox(self.window, textvariable=self.style_var, values=stylelist, state="readonly")
        style.pack()
        style_window =canvas_obj.create_window(culsel, row, anchor="w", window=style, width=scale(150), height=CBHEIGHT)
        canvas_obj.create_text(cultex, row + 1, text="Choose Style:", anchor="w", fill=outlinefont, font=textfont, tags=["outline"])
        canvas_obj.create_text(cultex, row, text="Choose Style:", anchor="w", fill=textcolor, font=textfont, tags=["text"])
        row += scale(40)

        # on/off scale with windows.
        self.w_scale_var = ttk.StringVar(master=window, value="Off")
        self.w_scale = ttk.Checkbutton(self.window, variable=self.w_scale_var, onvalue="On", offvalue="Off", bootstyle="success")
        w_scale_window = canvas_obj.create_window(culsel, row, anchor="w", window=self.w_scale)
        canvas_obj.create_text(cultex, row +1, text="Scale With Windows:", anchor="w", fill=outlinefont, font=textfont, tags=["outline"])
        canvas_obj.create_text(cultex, row, text="Scale With Windows:", anchor="w", fill=textcolor, font=textfont, tags=["text"])

        row += scale(40)

        # on/off Auto Backup
        self.backup_var = ttk.StringVar(master=window, value="Off")
        backup = ttk.Checkbutton(self.window, variable=self.backup_var, onvalue="On", offvalue="Off", bootstyle="success")
        backup_window = canvas_obj.create_window(culsel, row, anchor="w", window=backup)
        canvas_obj.create_text(cultex, row +1, text="Auto Backup:", anchor="w", fill=outlinefont, font=textfont, tags=["outline"])
        canvas_obj.create_text(cultex, row, text="Auto Backup:", anchor="w", fill=textcolor, font=textfont, tags=["text"])
        row += scale(40)

        # on/off Auto Backup for Cheats
        self.backup_cheat_var = ttk.StringVar(master=window, value="Off")
        backup_cheat = ttk.Checkbutton(self.window, variable=self.backup_cheat_var, onvalue="On", offvalue="Off", bootstyle="success")
        backup_cheat_window = canvas_obj.create_window(culsel, row, anchor="w", window=backup_cheat)
        canvas_obj.create_text(cultex, row +1, text="Auto Backup(Cheats):", anchor="w", fill=outlinefont, font=textfont, tags=["outline"])
        canvas_obj.create_text(cultex, row, text="Auto Backup(Cheats):", anchor="w", fill=textcolor, font=textfont, tags=["text"])
        row += scale(40)

        # on/off Animations
        self.ani_var = ttk.StringVar(master=window, value="Off")
        ani = ttk.Checkbutton(self.window, variable=self.ani_var, onvalue="On", offvalue="Off", bootstyle="success")
        ani_window = canvas_obj.create_window(culsel, row, anchor="w", window=ani)
        canvas_obj.create_text(cultex, row +1, text="Disable Animations:", anchor="w", fill=outlinefont, font=textfont, tags=["outline"])
        canvas_obj.create_text(cultex, row, text="Disable Animations:", anchor="w", fill=textcolor, font=textfont, tags=["text"])
        row += scale(40)

        apply = ttk.Button(self.window, text="Apply", command=lambda: self.saveconfig(canvases))
        apply_window = canvas_obj.create_window(cultex, row, anchor="w", window=apply, width=scale(65), height=scale(28))

        self.loadconfig()

    def saveconfig(self, canvases=None):
        print("font_var:", self.font_var.get())
        print("color_var:", self.color_var.get())
        print("style_var:", self.style_var.get())
        print("w_scale_var:", self.w_scale_var.get())
        print("backup_var:", self.backup_var.get())
        print("backup_cheat_var:", self.backup_cheat_var.get())
        print("ani_var:", self.ani_var.get())

        config = configparser.ConfigParser()
        config.read(localconfig)
        print(config)
        if not config.has_section("Settings"):
            config["Settings"] = {}
        config["Settings"]["font"] = self.font_var.get()
        config["Settings"]["color"] = self.color_var.get()
        config["Settings"]["style"] = self.style_var.get()
        config["Settings"]["scale"] = self.w_scale_var.get()
        config["Settings"]["backup"] = self.backup_var.get()
        config["Settings"]["cheat-backup"] = self.backup_cheat_var.get()
        config["Settings"]["animation"] = self.ani_var.get()

        with open(localconfig, 'w') as file:
            config.write(file)

        color = Color()
        new_font = (self.font_var.get(), 15)
        new_text_color = color.get(self.color_var.get())
        theme = self.style_var.get()
        self.style.theme_use(theme)
        try:
            for canvas in canvases:
                canvas.itemconfig("text", fill=new_text_color, font=new_font)
                canvas.itemconfig("outline", font=new_font)
        except AttributeError as e:
            print("S")

    def loadconfig(self):
        config = configparser.ConfigParser()
        config.read(localconfig)

        self.font_var.set(config.get("Settings", "font", fallback="Arial"))
        self.color_var.set(config.get("Settings", "color", fallback="light-cyan"))
        self.style_var.set(config.get("Settings", "style", fallback="flatly"))
        self.w_scale_var.set(config.get("Settings", "scale", fallback="Off"))
        self.backup_var.set(config.get("Settings", "backup", fallback="Off"))
        self.backup_cheat_var.set(config.get("Settings", "cheat-backup", fallback="On"))
        self.ani_var.set(config.get("Settings", "animation", fallback="On"))

    def get_setting(self, args):
        font = self.config.get("Settings", "font", fallback="Arial")
        color = self.config.get("Settings", "color", fallback="light-cyan")
        style = self.config.get("Settings", "style", fallback="flatly")
        w_scale = self.config.get("Settings", "scale", fallback="Off")
        backup = self.config.get("Settings", "backup", fallback="Off")
        cheat_backup = self.config.get("Settings", "cheat-backup", fallback="On")
        animation = self.config.get("Settings", "animation", fallback="On")
        if args in ["ani", "animation"]:
            return animation
        elif args in ["color", "c"]:
            return color
        elif args in ["font", "f"]:
            return font
        elif args in ["style", "s"]:
            return style
        elif args in ["ws", "scale"]:
            return w_scale
        elif args in ["backup", "b"]:
            return backup
        elif args in ["cheatbackup", "cheat_backup", "cb"]:
            return cheat_backup

    def createwindow(self):
        self.window = ttk.Window(scaling=sf)
        self.window.title(f"Optimizer Settings")
        window_width = scale(400)
        window_height = scale(400)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.window.resizable(False, False)