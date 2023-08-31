import threading
import tkinter

import ttkbootstrap as ttk
import webbrowser
import re
from tkinter import filedialog, Toplevel
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from modules.canvas import Canvas_Create
from modules.qt_config import modify_disabled_key, get_config_parser
from modules.checkpath import checkpath, DetectOS
from modules.backup import *
from modules.logger import *
from modules.config import save_user_choices, load_user_choices
from configuration.settings import *
from configuration.settings_config import Setting


class Manager:
    def __init__(self, window):
        # Define the Manager window.
        self.window = window

        # Configure the Style of the entire window.
        self.constyle = Style(theme=theme.lower())
        self.constyle.configure("TButton", font=btnfont)

        # Set initialize different Classes.
        self.on_canvas = Canvas_Create()
        self.setting = Setting()

        # Append all canvas in Manager class.
        self.all_canvas = []

        # Load the Config.
        self.config = localconfig

        # Read the Current Emulator Mode.
        self.mode = config.get("Mode", "managermode", fallback="Yuzu")

        # Set neccesary variables.
        self.Yuzudir = None
        self.is_Ani_running = False
        self.is_Ani_Paused = False
        self.tooltip_active = False
        self.warn_again = "yes"
        self.title_id = title_id
        self.old_cheats = {}
        self.cheat_version = ttk.StringVar(value="Version - 1.2.00")

        # Initialize Json Files.
        self.dfps_options = load_json("DFPS.json", dfpsurl)
        self.description = load_json("Description.json", descurl)
        self.presets = load_json("preset.json", presetsurl)
        self.version_options = load_json("Version.json", versionurl)
        self.cheat_options = load_json("Cheats.json", cheatsurl)

        # Local text variable
        self.switch_text = ttk.StringVar(value="Switch to Ryujinx")

        # Load Canvas
        self.Load_ImagePath()
        self.load_canvas()
        self.switchmode("false")

        #Window protocols
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.on_canvas.on_closing(self.window))

    def warning(self, e):
        messagebox.showwarning(f"{e}")

    def create_canvas(self):
        # Create Canvas
        self.maincanvas = ttk.Canvas(self.window, width=scale(1200), height=scale(600))
        canvas = self.maincanvas
        self.maincanvas.pack()
        self.all_canvas.append(self.maincanvas)

        # Load UI Elements
        self.load_UI_elements(self.maincanvas)
        self.create_tab_buttons(self.maincanvas)

        # Create Text Position
        row = 40
        cul_tex = 40
        cul_sel = 180

        # Run Scripts for checking OS and finding location
        checkpath(self, self.mode)
        DetectOS(self, self.mode)

        # FOR DEBUGGING PURPOSES
        def onCanvasClick(event):
            print(f"CRODS = X={event.x} + Y={event.y} + {event.widget}")
        self.maincanvas.bind("<Button-3>", onCanvasClick)
        # Start of CANVAS options.

        # Create preset menu.
        presets = {"Saved": {}} | load_json("preset.json", presetsurl)
        values = list(presets.keys())
        self.selected_preset = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Select Preset:",
                                                            variable=values[0], values=values,
                                                            row=row, cul=cul_tex,
                                                            tags=["text"], tag="Yuzu",
                                                            description_name="Presets",
                                                            command=self.apply_selected_preset
                                                        )

        # Setting Preset - returns variable.
        value = ["No Change", "Steamdeck", "AMD", "Nvidia", "High End Nvidia"]
        self.selected_settings = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Select Settings:",
                                                            variable=value[0], values=value,
                                                            row=row, cul=340, drop_cul=480,
                                                            tags=["text"], tag="yuzu",
                                                            description_name="Settings"
                                                        )

        row += 40
        # Create a label for yuzu.exe selection
        backupbutton = cul_sel
        if self.os_platform == "Windows":
            self.on_canvas.create_button(
                                        master=self.window, canvas=canvas,
                                        btn_text="Browse",
                                        row=row, cul=cul_sel, width=6,
                                        tags=["Button"],
                                        description_name="Browse",
                                        command=self.select_yuzu_exe
                                        )


            # Reset to Appdata
            def yuzu_appdata():
                checkpath(self, self.mode)
                log.info("Successfully Defaulted to Appdata!")
                save_user_choices(self, self.config, "appdata", None)

            self.on_canvas.create_button(
                                        master=self.window, canvas=canvas,
                                        btn_text="Use Appdata",
                                        row=row, cul=cul_sel + 68, width=9,
                                        tags=["Button", "yuzu"],
                                        description_name="Reset",
                                        command=yuzu_appdata
                                        )
            backupbutton = cul_sel + 165
            text = "Select Yuzu.exe"
            command = lambda event: self.select_yuzu_exe()
        else:
            text = "Backup Save Files"
            command = None
        self.on_canvas.create_label(
                                    master=self.window, canvas=canvas,
                                    text=text,
                                    description_name="Browse",
                                    row=row, cul=cul_tex,
                                    tags=["text"], tag=["Select-EXE"], outline_tag="outline",
                                    command=command
                                    )

        # Create a Backup button
        self.on_canvas.create_button(
                                    master=self.window, canvas=canvas,
                                    btn_text="Backup",
                                    row=row, cul=backupbutton, width=7,
                                    tags=["Button", "yuzu"],
                                    description_name="Backup",
                                    command=lambda: backup(self)
        )

        self.on_canvas.create_button(
                                    master=self.window, canvas=canvas,
                                    btn_text="Clear Shaders",
                                    row=row, cul=backupbutton+78, width=9,
                                    tags=["Button", "yuzu"],
                                    description_name="Shaders",
                                    command=lambda: clean_shaders(self)
        )
        row += 40

        # Create big TEXT label.
        self.on_canvas.create_label(
                                    master=self.window, canvas=canvas,
                                    text="Display Settings", font=bigfont, color=BigTextcolor,
                                    description_name="Display Settings",
                                    row=row, cul=cul_tex+100,
                                    tags=["Big-Text"]
                                    )

        self.on_canvas.create_label(
                                    master=self.window, canvas=canvas,
                                    text="Mod Improvements", font=bigfont, color=BigTextcolor,
                                    description_name="Mod Improvements",
                                    row=row, cul=400+100,
                                    tags=["Big-Text"]
                                    )
        row += 40

        # Create a label for resolution selection

        self.DFPS_var = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Dynamic FPS Version:",
                                                            variable=DFPS_list[0], values=DFPS_list,
                                                            row=row, cul=cul_tex, drop_cul=cul_sel,
                                                            tags=["text"], tag=None,
                                                            description_name="DFPS",
                                                            command=lambda event: self.warning_window("Res")
                                                            )
        row += 40

        values = self.dfps_options.get("ResolutionNames", [])
        self.resolution_var = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Select a Resolution:",
                                                            variable=value[0], values=values,
                                                            row=row, cul=cul_tex, drop_cul=cul_sel,
                                                            tags=["text"], tag=None,
                                                            description_name="Resolution",
                                                            command=lambda event: self.warning_window("Res")
                                                            )
        row += 40

        self.aspect_ratio_var = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Screen Aspect Ratio:",
                                                            variable=AR_list[0], values=AR_list,
                                                            row=row, cul=cul_tex, drop_cul=cul_sel,
                                                            tags=["text"], tag=None,
                                                            description_name="Aspect Ratio",
                                                            )
        row += 40

        # Create a label for FPS selection
        values = self.dfps_options.get("FPS", [])
        self.fps_var = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Select an FPS:",
                                                            variable=value[0], values=values,
                                                            row=row, cul=cul_tex, drop_cul=cul_sel,
                                                            tags=["text"], tag=None,
                                                            description_name="FPS"
                                                      )

        row += 40

        # Create a label for shadow resolution selection
        values = self.dfps_options.get("ShadowResolutionNames", [""])
        self.shadow_resolution_var = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Shadow Resolution:",
                                                            variable=value[0], values=values,
                                                            row=row, cul=cul_tex, drop_cul=cul_sel,
                                                            tags=["text"], tag=None,
                                                            description_name="Shadows"
                                                                    )
        row += 40

        # Make exception for camera quality
        values = self.dfps_options.get("CameraQualityNames", [""])
        for index, value in enumerate(values):
            if value in ["Enable", "Enabled"]:
                values[index] = "On"
            elif value in ["Disable", "Disabled"]:
                values[index] = "Off"

        self.camera_var = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Camera Quality++:",
                                                            variable=value[0], values=values,
                                                            row=row, cul=cul_tex, drop_cul=cul_sel,
                                                            tags=["text"], tag=None,
                                                            description_name="Camera Quality"
                                                        )
        row += 40

        # Create a label for UI selection
        self.ui_var = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Select an UI:",
                                                            variable=UI_list[0], values=UI_list,
                                                            row=row, cul=cul_tex, drop_cul=cul_sel,
                                                            tags=["text"], tag=None,
                                                            description_name="UI"
                                                    )
        row += 40

        # First Person and FOV
        self.fp_var = self.on_canvas.create_combobox(
                                                        master=self.window, canvas=canvas,
                                                        text="Enable First Person:",
                                                        values=FP_list, variable=FP_list[0],
                                                        row=row, cul=cul_tex, drop_cul=cul_sel,
                                                        tags=["text"], tag=None,
                                                        description_name="First Person"
                                                    )
        # XYZ to generate patch.

        row =120
        cul_tex = 400
        cul_sel = 550

        # Create labels and enable/disable options for each entry
        self.selected_options = {}
        for version_option_name, version_option_value in self.version_options[0].items():

            # Create label
            if version_option_name not in ["Source", "nsobid", "offset", "version"]:

                # Create checkbox
                version_option_var = self.on_canvas.create_checkbutton(
                                                                        master=self.window, canvas=canvas,
                                                                        text=version_option_name,
                                                                        variable="Off",
                                                                        row=row + 40, cul=cul_tex, drop_cul=cul_sel,
                                                                        tags=["text"], tag=None,
                                                                        description_name=version_option_name
                                                                       )
                self.selected_options[version_option_name] = version_option_var
                row += 40

            if row >= 480:
                row = 20
                cul_tex += 180
                cul_sel += 180

        # Create a submit button
        self.on_canvas.create_button(
            master=self.window, canvas=canvas,
            btn_text="Apply Mods", tags=["Button"],
            row=520, cul=39, padding=10, width=9,
            description_name="Apply", style="success",
            command=self.submit
        )
        # Load Saved User Options.
        load_user_choices(self, self.config)
        return self.maincanvas

    def create_cheat_canvas(self):
        # Create Cheat Canvas
        self.cheatcanvas = ttk.Canvas(self.window, width=scale(1200), height=scale(600))
        self.cheatcanvas.pack(expand=1, fill=BOTH)
        canvas = self.cheatcanvas
        self.all_canvas.append(self.cheatcanvas)

        # Create UI elements.
        self.Cheat_UI_elements(self.cheatcanvas)
        self.create_tab_buttons(self.cheatcanvas)

        # Push every version in combobox
        versionvalues = []
        for each in self.cheat_options:
            for key, value in each.items():
                if key == "Aversion":
                    versionvalues.append("Version - " + value)

        self.cheat_version = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="",
                                                            values=versionvalues, variable=versionvalues[1],
                                                            row=520, cul=130+2, drop_cul=130+2,
                                                            tags=["text"], tag=None,
                                                            description_name="CheatVersion",
                                                            command=lambda event: loadCheats()
                                                            )
        load_user_choices(self, self.config)


        def loadCheats():
            row = 40
            cul_tex = 40
            cul_sel = 200

            corrent_cheats = self.cheat_options[versionvalues.index(self.cheat_version.get())].items()
            corrent_cheats_dict = dict(corrent_cheats)
            sorted_cheats = dict(sorted(corrent_cheats_dict.items(), key=lambda item: item[0]))
            try:
                for key_var, value in self.selected_cheats.items():
                    value = value.get()
                    self.old_cheats[key_var] = value
            except AttributeError as e:
                self.old_cheats = {}

            self.selected_cheats = {}

            self.cheatcanvas.delete("cheats")

            for version_option_name, version_option_value in sorted_cheats.items():
                # Exclude specific keys from being displayed
                if version_option_name in ["Source", "nsobid", "offset", "version"]:
                    continue

                # Create label
                if version_option_name not in ["Source", "Version", "Aversion", "Cheat Example"]:

                    version_option_var = self.on_canvas.create_checkbutton(
                        master=self.window, canvas=canvas,
                        text=version_option_name,
                        variable="Off",
                        row=row, cul=cul_tex, drop_cul=cul_sel,
                        tags=["text"], tag="cheats",
                        description_name=version_option_name
                    )

                    # Create enable/disable dropdown menu
                    try:
                        if self.old_cheats.get(version_option_name) == "On":
                            version_option_var.set("On")
                    except AttributeError as e:
                        self.old_cheats = {}
                    self.selected_cheats[version_option_name] = version_option_var
                else:
                    continue

                row += 40

                if row > 480:
                    row = 40
                    cul_tex += 200
                    cul_sel += 200


        def ResetCheats():
            try:
                for key, value in self.selected_cheats.items():
                    value.set("Off")
            except AttributeError as e:
                log.error(f"Error found from ResetCheats, the script will continue. {e}")


        # Create a submit button
        self.on_canvas.create_button(
                                    master=self.window, canvas=canvas,
                                    btn_text="Apply Cheats",
                                    row=520, cul=39, width=9, padding=5,
                                    tags=["Button"],
                                    style="success",
                                    description_name="Apply Cheats",
                                    command=lambda: self.submit("Cheats")
        )

        # Create a submit button
        self.on_canvas.create_button(
                                    master=self.window, canvas=canvas,
                                    btn_text="Reset Cheats",
                                    row=520, cul=277+6+2, width=8, padding=5,
                                    tags=["Button"],
                                    style="default",
                                    description_name="Reset Cheats",
                                    command=ResetCheats
        )
        # Read Cheats
        self.on_canvas.create_button(
                                    master=self.window, canvas=canvas,
                                    btn_text="Read Saved Cheats",
                                    row=520, cul=366+2, width=11, padding=5,
                                    tags=["Button"],
                                    style="default",
                                    description_name="Read Cheats",
                                    command=lambda: load_user_choices(self, self.config, "Cheats")
        )

        #Backup
        self.on_canvas.create_button(
                                    master=self.window, canvas=canvas,
                                    btn_text="Backup",
                                    row=520, cul=479+2, width=7, padding=5,
                                    tags=["Button"],
                                    style="default",
                                    description_name="Backup",
                                    command=lambda: backup(self)
        )
        loadCheats()
        load_user_choices(self, self.config)

    def show_main_canvas(self):
        self.on_canvas.is_Ani_Paused = True
        self.cheatcanvas.pack_forget()
        self.maincanvas.pack()

    def show_cheat_canvas(self):
        self.on_canvas.is_Ani_Paused = False
        self.cheatcanvas.pack()
        self.maincanvas.pack_forget()

        self.ani = threading.Thread(name="cheatbackground",
                                    target=lambda: self.on_canvas.canvas_animation(self.window, self.cheatcanvas))
        if not self.is_Ani_running == True:
            self.is_Ani_running = True
            self.ani.start()

    def open_browser(self, web, event=None):
        url = "https://ko-fi.com/maxlastbreath#"
        if web == "Kofi":
            url = "https://ko-fi.com/maxlastbreath#"
        elif web == "Github":
            url = "https://github.com/MaxLastBreath/TOTK-mods"
        elif web == "Discord":
            url = "https://discord.gg/7MMv4yGfhM"
        webbrowser.open(url)
        return

    def load_canvas(self):
        # Main
        self.create_canvas()
        self.create_cheat_canvas()
        self.cheatcanvas.pack_forget()

    def Load_ImagePath(self):
        # Create a Gradiant for Yuzu.
        self.background_YuzuBG = self.on_canvas.Photo_Image(
            image_path="Yuzu_BG.png",
            width=1200, height=600,
        )

        # Create a Gradiant for Ryujinx.
        self.background_RyuBG = self.on_canvas.Photo_Image(
            image_path="Ryujinx_BG.png",
            width=1200, height=600,
        )

        # UI Elements/Buttons
        self.master_sword_element = self.on_canvas.Photo_Image(
            image_path="Master_Sword.png",
            width=155, height=88,
        )
        self.master_sword_element2 = self.on_canvas.Photo_Image(
            image_path="Master_Sword2.png", mirror=True,
            width=155, height=88,
        )

        self.master_sword_element_active = self.on_canvas.Photo_Image(
            image_path="Master_Sword_active.png",
            width=155, height=88,
        )

        self.master_sword_element2_active = self.on_canvas.Photo_Image(
            image_path="Master_Sword_active2.png", mirror=True,
            width=155, height=88,
        )

        self.hylian_element = self.on_canvas.Photo_Image(
            image_path="Hylian_Shield.png",
            width=72, height=114,
        )

        self.hylian_element_active = self.on_canvas.Photo_Image(
            image_path="Hylian_Shield_Active.png",
            width=72, height=114,
        )

        self.background_UI_element = self.on_canvas.Photo_Image(
            image_path="BG_Left_2.png",
            width=1200, height=600,
        )

        # Create Gradiant for cheats.
        self.background_Cheats = self.on_canvas.Photo_Image(
            image_path="BG_Cheats.png",
            width=1200, height=600,
        )

        # Create a transparent black background
        self.background_UI2 = self.on_canvas.Photo_Image(
            image_path="BG_Right.png",
            width=1200, height=600,
        )

        # Create a Gradiant background.
        self.background_UI = self.on_canvas.Photo_Image(
            image_path="BG_Left.png",
            width=1200, height=600,
        )

        # Create a transparent black background
        self.background_UI3 = self.on_canvas.Photo_Image(
            image_path="BG_Right_UI.png",
            width=1200, height=600,
        )

        # Attempt to load images from custom folder.
        if os.path.exists("custom/bg.jpg"):
            image_path = "custom/bg.jpg"
        elif os.path.exists("custom/bg.png"):
            image_path = "custom/bg.png"
        else:
            # Load and set the image as the background
            image_path ="image.png"

        self.background_image = self.on_canvas.Photo_Image(
            image_path=image_path,
            width=1200, height=600,
            blur=1
        )
        if os.path.exists("custom/cbg.jpg"):
            image_path = "custom/cbg.jpg"
        elif os.path.exists("custom/cbg.png"):
            image_path = "custom/cbg.png"

        self.blurbackground = self.on_canvas.Photo_Image(
            image_path=image_path,
            width=1200, height=600, img_scale=2.0,
            blur=3
        )

        # Handle Text Window
        def fetch_text_from_github(file_url):
            try:
                response = requests.get(file_url)
                if response.status_code == 200:
                    return response.text
                else:
                    log.error("Error: Unable to fetch text from Github")
            except requests.exceptions.RequestException as e:
                log.error(f"Error occurred while fetching text: {e}")

            return ""
        # Information text
        file_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/Announcements/Announcement%20Window.txt"
        self.text_content = fetch_text_from_github(file_url)
        # Info Element

    def load_UI_elements(self, canvas):
        # Images and Effects
        canvas.create_image(0, 0, anchor="nw", image=self.background_image, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_YuzuBG, tags="overlay-1")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI, tags="overlay")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI_element, tags="overlay")

        # Info text BG
        canvas.create_image(0-scale(20), 0, anchor="nw", image=self.background_UI2, tags="overlay")
        canvas.create_image(0-scale(20), 0, anchor="nw", image=self.background_UI3, tags="overlay")

        # Create Active Buttons.
        self.on_canvas.image_Button(
            canvas=canvas,
            row=182, cul=794,
            img_1=self.master_sword_element, img_2=self.master_sword_element_active,
            command=lambda event: self.open_browser("Kofi")
        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=182, cul=1007,
            img_1=self.master_sword_element2, img_2=self.master_sword_element2_active,
            command=lambda event: self.open_browser("Github")
        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=240, cul=978, anchor="c",
            img_1=self.hylian_element, img_2=self.hylian_element_active,
            command=lambda event: self.open_browser("Discord")
        )

        # Information text.
        text_widgetoutline2 = canvas.create_text(scale(1001) - scale(20), scale(126) -scale(80), text=f"{self.mode} TOTK Optimizer", tags="information", fill="black", font=biggyfont, anchor="center", justify="center", width=scale(325))
        text_widget2 = canvas.create_text(scale(1000)-scale(20), scale(126)-scale(80), text=f"{self.mode} TOTK Optimizer", tags="information", fill="#FBF8F3", font=biggyfont, anchor="center", justify="center", width=scale(325))

        text_widgetoutline1 = canvas.create_text(scale(1001) -scale(20) -scale(10), scale(126) + scale(10), text=self.text_content, fill="black", font=biggyfont, anchor="center", justify="center", width=scale(325))
        text_widget1 = canvas.create_text(scale(1000) - scale(20) -scale(10), scale(125) +scale(10), text=self.text_content, fill="#FBF8F3", font=biggyfont, anchor="center", justify="center", width=scale(325))

    def Cheat_UI_elements(self, canvas):
        self.cheatbg = canvas.create_image(0, -scale(300), anchor="nw", image=self.blurbackground, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_YuzuBG, tags="overlay-1")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI, tags="overlay")

    def create_tab_buttons(self, canvas):

        if not canvas == self.maincanvas:
            # Kofi Button
            self.on_canvas.create_button(
                master=self.window, canvas=canvas,
                btn_text="Donate", textvariable=self.switch_text,
                style="success",
                row=1130, cul=520, width=60, padding=10, pos="center",
                tags=["Button"],
                description_name="Kofi",
                command=lambda: self.open_browser("Kofi")
            )
            # Github Button
            self.on_canvas.create_button(
                master=self.window, canvas=canvas,
                btn_text="Github", textvariable=self.switch_text,
                style="success",
                row=1066, cul=520, width=60, padding=10, pos="center",
                tags=["Button"],
                description_name="Github",
                command=lambda: self.open_browser("Github")
            )

        # Create tabs

        # Switch mode between Ryujinx and Yuzu
        self.on_canvas.create_button(
            master=self.window, canvas=canvas,
            btn_text="Switch", textvariable=self.switch_text,
            style="Danger",
            row=11, cul=138, width=12,
            tags=["Button"],
            description_name="Switch",
            command=self.switchmode
        )
        # Make the button active for current canvas.
        button1style = "default"
        button2style = "default"
        button3style = "default"
        active_button_style = "secondary"
        try:
            if canvas == self.maincanvas:
                button1style = active_button_style
            if canvas == self.cheatcanvas:
                button2style = active_button_style
        except AttributeError as e:
            e = "n"

        # 1 - Main
        self.on_canvas.create_button(
            master=self.window, canvas=canvas,
            btn_text="Main",
            style=button1style,
            row=11, cul=26, width=5,
            tags=["Button"],
            description_name="Main",
            command=self.show_main_canvas
        )
        # 2 - Cheats
        self.on_canvas.create_button(
            master=self.window, canvas=canvas,
            btn_text="Cheats",
            style=button2style,
            row=11, cul=77, width=6,
            tags=["Button"],
            description_name="Cheats",
            command=self.show_cheat_canvas
        )
        # 3 - Settings
        self.on_canvas.create_button(
            master=self.window, canvas=canvas,
            btn_text="Settings",
            style=button3style,
            row=11, cul=257, width=8,
            tags=["Button"],
            description_name="Settings",
            command=lambda: self.setting.settingswindow(self.constyle, self.all_canvas)
        )

    def switchmode(self, command="true"):
        if command == "true":
            if self.mode == "Yuzu":
                self.mode = "Ryujinx"
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Select-EXE", text=f"Select Ryujinx.exe")
                    canvas.itemconfig("yuzu", state="hidden")
                self.switch_text.set("Switch to Yuzu")
                return
            elif self.mode == "Ryujinx":
                self.mode = "Yuzu"
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_YuzuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Select-EXE", text=f"Select Yuzu.exe")
                    canvas.itemconfig("yuzu", state="normal")
                # change text
                self.switch_text.set("Switch to Ryujinx")
                return
        elif command == "false":
            if self.mode == "Ryujinx":
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Select-EXE", text=f"Select Ryujinx.exe")
                    canvas.itemconfig("yuzu", state="hidden")
                self.switch_text.set("Switch to Yuzu")
                return
        elif command == "Mode":
            return self.mode

    def apply_selected_preset(self, event=None):
        try:
            selected_preset = self.selected_preset.get()
        except AttributeError as e:
            selected_preset = "Saved"
            log.error(f"Failed to apply selected preset: {e}")

        if selected_preset == "None":
            if os.path.exists(self.config):
                load_user_choices(self, self.config)
            else:
                # Fallback to the default preset
                default_preset = self.get_local_presets().get("Default", {})
                self.apply_preset(default_preset)

        elif selected_preset == "Saved":
            if os.path.exists(self.config):
                load_user_choices(self, self.config)
            else:
                messagebox.showinfo("Saved Preset", "No saved preset found. Please save your current settings first.")
        elif selected_preset in self.presets:
            preset_to_apply = self.presets[selected_preset]
            for key, value in preset_to_apply.items():
                if value.lower() in ["enable", "enabled", "on"]:
                    preset_to_apply[key] = "On"
                elif value.lower() in ["disable", "disabled", "off"]:
                    preset_to_apply[key] = "Off"
            # Apply the selected preset from the online presets
            self.apply_preset(self.presets[selected_preset])

    def apply_preset(self, preset_options):
        self.resolution_var.set(preset_options.get("Resolution", ""))
        self.fps_var.set(preset_options.get("FPS", ""))
        self.shadow_resolution_var.set(preset_options.get("ShadowResolution", ""))
        self.camera_var.set(preset_options.get("CameraQuality", ""))
        self.ui_var.set(preset_options.get("UI", ""))
        self.fp_var.set(preset_options.get("First Person", ""))

        skip_keys = ["Resolution", "FPS", "ShadowResolution", "CameraQuality", "UI"]

        for option_key, option_value in preset_options.items():
            # Check if the option exists in the self.selected_options dictionary and not in the skip_keys
            if option_key in self.selected_options and option_key not in skip_keys:
                self.selected_options[option_key].set(option_value)
            else:
                continue

    # Select Yuzu Dir
    def select_yuzu_exe(self):
        # Open a file dialog to browse and select yuzu.exe
        if self.os_platform == "Windows":
            yuzu_path = filedialog.askopenfilename(
                filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
            )
            home_directory = os.path.dirname(self.yuzu_path)
            Default_Yuzu_Directory = os.path.join(home_directory, "user")
            Default_Ryujinx_Directory = os.path.join(home_directory, "portable")
            executable_name = yuzu_path
            if executable_name.endswith("Ryujinx.exe"):
                if self.mode == "Yuzu":
                    self.switchmode("true")
            if executable_name.endswith("yuzu.exe"):
                if self.mode == "Ryujinx":
                    self.switchmode("true")
            if yuzu_path:
                # Save the selected yuzu.exe path to a configuration file
                save_user_choices(self, self.config, yuzu_path)
                home_directory = os.path.dirname(yuzu_path)
                if os.path.exists(Default_Yuzu_Directory) or os.path.exists(Default_Ryujinx_Directory):
                    log.info(f"Successfully selected {self.mode}.exe! And a portable folder was found at {home_directory}!")
                    checkpath(self, self.mode)
                else:
                    log.info(f"Portable folder for {self.mode} not found defaulting to appdata directory!")
                    checkpath(self, self.mode)

                # Update the yuzu.exe path in the current session
                self.yuzu_path = yuzu_path
            else:
                checkpath(self, self.mode)
            # Save the selected yuzu.exe path to a configuration file
            save_user_choices(self, self.config, yuzu_path)
        return
    # Load Yuzu Dir
    def load_yuzu_path(self, config_file):
        if self.mode == "Yuzu":
            config = configparser.ConfigParser()
            config.read(config_file)
            yuzu_path = config.get('Paths', 'yuzupath', fallback="Appdata")
            return yuzu_path
        if self.mode == "Ryujinx":
            config = configparser.ConfigParser()
            config.read(config_file)
            ryujinx_path = config.get('Paths', 'ryujinxpath', fallback="Appdata")
            return ryujinx_path
    # Download Manager

    def warning_window(self, setting_type):
        if self.mode == "Ryujinx":
            return
        warning_message = None
        configfile = self.TOTKconfig
        config = configparser.ConfigParser()
        config.read(configfile)

        if setting_type == "Res":
            resolution = self.resolution_var.get()
            Res_index = self.dfps_options.get("ResolutionNames").index(resolution)
            current_res = self.dfps_options.get("ResolutionValues", [""])[Res_index].split("x")[1]
            proper_res = float(current_res)

            newmem1 = config.get("Core", "memory_layout_mode\\use_global", fallback="true")
            newmem2 = config.get("Core", "memory_layout_mode\\default", fallback="true")
            newmemsetting = int(config.get("Core", "memory_layout_mode", fallback=0)) # 0 - 4gb, 1 - 6gb, 2 - 8gb
            res1 = config.get("Renderer", "resolution_setup\\use_global", fallback="true")
            res2 = config.get("Renderer", "resolution_setup\\default", fallback="true")
            res3 = int(config.get("Renderer", "resolution_setup", fallback=0))

            if 1080 < proper_res < 2160:
                if newmemsetting < 1 or not res3 == 2 or not newmem1 == "false" or not newmem2 == "false":
                    warning_message = f"Resolution {resolution}, requires 1x Yuzu renderer and extended memory layout 6GB to be enabled, otherwise it won't function properly and will cause artifacts, you currently have them disabled, do you want to enable them?"
                else:
                    log.info("Correct settings are already applied, no changes required!!")
            elif proper_res > 2160:
                if newmemsetting < 2 or not res3 == 2 or not newmem1 == "false" or not newmem2 == "false":
                    warning_message = f"Resolution {resolution}, requires 1x Yuzu renderer and extended memory layout 8GB to be enabled, otherwise it won't function properly and will cause artifacts, you currently have them disabled, do you want to enable them?"
                else:
                    log.info("Correct settings are already applied, no changes required!!")

        if warning_message is not None and warning_message.strip():
            response = messagebox.askyesno(f"WARNING! Required settings NOT Enabled!", warning_message)
            # If Yes, Modify the Config File.
            if response:
                # Remove existing options in Renderer section
                if not config.has_section("Renderer"):
                    config["Renderer"] = {}
                config["Renderer"]["resolution_setup\\use_global"] = "false"
                config["Renderer"]["resolution_setup\\default"] = "false"
                config["Renderer"]["resolution_setup"] = "2"

                # Core section
                if not config.has_section("Core"):
                    config["Core"] = {}
                config["Core"]["use_unsafe_extended_memory_layout\\use_global"] = "false"
                config["Core"]["use_unsafe_extended_memory_layout\\default"] = "false"
                config["Core"]["use_unsafe_extended_memory_layout\\default"] = "true"

                config["Core"]["memory_layout_mode\\use_global"] = "false"
                config["Core"]["memory_layout_mode\\default"] = "false"
                layout = "1"
                if proper_res > 2160:
                    layout = "2"

                config["Core"]["memory_layout_mode"] = layout

                with open(configfile, "w") as configfile:
                    config.write(configfile, space_around_delimiters=False)
            else:
                # If No, do nothing.
                log.info(f"Turning on required settings declined!!")

    # Submit the results, run download manager. Open a Loading screen.
    def submit(self, mode=None):
        self.add_list = []
        self.remove_list = []
        checkpath(self, self.mode)
        # Needs to be run after checkpath.
        if self.mode == "Yuzu":
            qtconfig = get_config_parser()
            qtconfig.optionxform = lambda option: option
            qtconfig.read(self.configdir)
        else:
            qtconfig = None

        def timer(value):
            progress_bar["value"] = value
            self.window.update_idletasks()

        def run_tasks():
            if mode == "Cheats":
                log.info("Starting TASKs for Cheat Patch..")
                tasklist = [Create_Mod_Patch("Cheats")]
                if get_setting("cheat-backup") in ["On"]:
                    tasklist.append(backup(self))
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                progress_window.destroy()
                return
            if mode== None:
                log.info("Starting TASKs for Normal Patch..")
                tasklist = [DownloadFP(), DownloadUI(), DownloadDFPS(), Create_Mod_Patch(), UpdateSettings(), Disable_Mods()]
                if get_setting("auto-backup") in ["On"]:
                    tasklist.append(backup(self))
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                progress_window.destroy()
                return

        def Create_Mod_Patch(mode=None):
            save_user_choices(self, self.config)

            if mode == "Cheats":
                log.info("Starting Cheat patcher.")
                self.progress_var.set("Creating Cheat ManagerPatch.")
                save_user_choices(self, self.config, None, "Cheats")
                selected_cheats = {}
                for option_name, option_var in self.selected_cheats.items():
                    selected_cheats[option_name] = option_var.get()
                # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Yuzu together.
                for version_option in self.cheat_options:
                    version = version_option.get("Version", "")
                    mod_path = os.path.join(self.load_dir, "Cheat Manager Patch", "cheats")

                    # Create the directory if it doesn't exist
                    os.makedirs(mod_path, exist_ok=True)

                    filename = os.path.join(mod_path, f"{version}.txt")
                    all_values = []
                    try:
                        with open(filename, "w") as file:
                            file.flush()
                            # file.write(version_option.get("Source", "") + "\n") - makes cheats not work
                            for key, value in version_option.items():
                                if key not in ["Source", "Aversion", "Version"] and selected_cheats[key] == "Off":
                                    continue
                                if key in selected_cheats:
                                        file.write(value + "\n")
                    except Exception as e:
                        log.error(f"ERROR! FAILED TO CREATE CHEAT PATCH. {e}")
                self.remove_list.append("Cheat Manager Patch")
                log.info("Applied cheats successfully.")
                return

            elif mode == None:
                log.info("Starting Mod Creator.")
                # Update progress bar
                self.progress_var.set("Creating Mod ManagerPatch.")
                resolution = self.resolution_var.get()
                fps = self.fps_var.get()
                shadow_resolution = self.shadow_resolution_var.get()
                camera_quality = self.camera_var.get()

                # Ensures that the patches are active and ensure that old versions of the mod folder is disabled.
                self.remove_list.extend(["DFPS", "Mod Manager Patch"])
                self.add_list.append("Visual Improvements")

                # Determine the path to the INI file in the user's home directory
                ini_file_directory = os.path.join(self.load_dir, "Mod Manager Patch", "romfs", "dfps")
                os.makedirs(ini_file_directory, exist_ok=True)
                ini_file_path = os.path.join(ini_file_directory, "default.ini")

                # Remove the previous default.ini file if it exists - DFPS settings.
                if os.path.exists(ini_file_path):
                    os.remove(ini_file_path)

                # Save the selected options to the INI file
                config = configparser.ConfigParser()
                config.optionxform = lambda option: option

                # Add the selected resolution, FPS, shadow resolution, and camera quality
                Resindex = self.dfps_options.get("ResolutionNames").index(resolution)
                ShadowIndex = self.dfps_options.get("ShadowResolutionNames").index(shadow_resolution)
                CameraIndex = self.dfps_options.get("CameraQualityNames").index(camera_quality)

                config['Graphics'] = {
                    'ResolutionWidth': self.dfps_options.get("ResolutionValues", [""])[Resindex].split("x")[0],
                    'ResolutionHeight': self.dfps_options.get("ResolutionValues", [""])[Resindex].split("x")[1],
                    'ResolutionShadows': self.dfps_options.get("ShadowResolutionValues", [""])[ShadowIndex]
                }
                config['dFPS'] = {'MaxFramerate': fps}
                config['Features'] = {'EnableCameraQualityImprovement': self.dfps_options.get("CameraQualityValues", [""])[CameraIndex]}

                selected_options = {}

                for option_name, option_var in self.selected_options.items():
                    selected_options[option_name] = option_var.get()
                # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Yuzu together.
            try:
                for version_option in self.version_options:
                    version = version_option.get("version", "")
                    mod_path = os.path.join(self.load_dir, "Mod Manager Patch", "exefs")

                    # Create the directory if it doesn't exist
                    os.makedirs(mod_path, exist_ok=True)

                    filename = os.path.join(mod_path, f"{version}.pchtxt")
                    all_values = []
                    with open(filename, "w") as file:
                        file.write(version_option.get("Source", "") + "\n")
                        file.write(version_option.get("nsobid", "") + "\n")
                        file.write(version_option.get("offset", "") + "\n")
                        for key, value in version_option.items():
                            if key not in ["Source", "nsobid", "offset", "version", "Version"] and not self.selected_options[key].get() == "Off":
                                pattern = r"@enabled\n([\da-fA-F\s]+)\n@stop"
                                matches = re.findall(pattern, value)
                                for match in matches:
                                    hex_values = match.strip().split()
                                    all_values.extend(hex_values)
                                    # Print @enabled and then @stop at the end.
                        file.write("@enabled\n")
                        for i, value in enumerate(all_values):
                            file.write(value)
                            if i % 2 == 1 and i != len(all_values) - 1:
                                file.write("\n")
                            else:
                                file.write(" ")
                        file.write("\n@stop\n")
                # Update Visual Improvements MOD.
                with open(ini_file_path, 'w') as configfile:
                    config.write(configfile)
            except PermissionError as e:
                log.error(f"FAILED TO CREATE MOD PATCH: {e}")

        def UpdateSettings():
            Setting_folder = None
            SettingGithubFolder = None
            Setting_selection = self.selected_settings.get()
            if Setting_selection == "No Change":
                log.info("Settings selection is None. Returning!")
                return
            elif Setting_selection == "Steamdeck":
                     Setting_folder = "Steamdeck"
                     SettingGithubFolder = "scripts/settings/Applied%20Settings/Steamdeck/0100F2C0115B6000.ini"
                     log.info("Installing steamdeck Yuzu preset")
            elif Setting_selection == "AMD":
                     Setting_folder = "AMD"
                     SettingGithubFolder = 'scripts/settings/Applied%20Settings/AMD/0100F2C0115B6000.ini'
                     log.info("Installing AMD Yuzu Preset")
            elif Setting_selection == "Nvidia":
                     Setting_folder = "Nvidia"
                     SettingGithubFolder = 'scripts/settings/Applied%20Settings/Nvidia/0100F2C0115B6000.ini'
                     log.info("Installing Nvidia Yuzu Preset")
            elif Setting_selection == "High End Nvidia":
                     Setting_folder = "High End Nvidia"
                     SettingGithubFolder = 'scripts/settings/Applied%20Settings/High%20End%20Nvidia/0100F2C0115B6000.ini'
                     log.info("Installing High End Nvidia Yuzu Preset")

            if Setting_selection is not None:
                    self.progress_var.set(f"Downloading and applying settings for {Setting_selection}.")
                    Setting_directory = self.TOTKconfig
                    raw_url = f'{repo_url_raw}/raw/main/{SettingGithubFolder}'
                    response = requests.get(raw_url)
                    if response.status_code == 200:
                        try:
                            with open(Setting_directory, "wb") as file:
                                file.write(response.content)
                        except Exception as e:
                            log.error(f"FAILED TO CREATE SETTINGS FILE: {e}")
                        log.info("Successfully Installed TOTK Yuzu preset settings!")
                        resolution = self.resolution_var.get()
                        Resindex = self.dfps_options.get("ResolutionNames").index(resolution)
                        current_res = self.dfps_options.get("ResolutionValues", [""])[Resindex].split("x")[1]
                        proper_res = float(current_res)
                        new_config = configparser.ConfigParser()
                        new_config.read(Setting_directory)
                    else:
                        log.error(f"Failed to download file from {raw_url}. Status code: {response.status_code}")
                        return
                    if proper_res > 1080:
                        # Add new values
                        if not new_config.has_section("Renderer"):
                            new_config["Renderer"] = {}
                        new_config["Renderer"]["resolution_setup\\use_global"] = "false"
                        new_config["Renderer"]["resolution_setup\\default"] = "false"
                        new_config["Renderer"]["resolution_setup"] = "2"

                        if not new_config.has_section("Core"):
                            new_config["Core"] = {}
                        new_config["Core"]["use_unsafe_extended_memory_layout\\use_global"] = "false"
                        new_config["Core"]["use_unsafe_extended_memory_layout\\default"] = "false"
                        new_config["Core"]["use_unsafe_extended_memory_layout\\default"] = "true"

                        new_config["Core"]["memory_layout_mode\\use_global"] = "false"
                        new_config["Core"]["memory_layout_mode\\default"] = "false"
                        layout = "1"
                    if proper_res >= 2160:
                        layout = "2"
                    elif proper_res <= 1080:
                        layout = "0"
                    new_config["Core"]["memory_layout_mode\\use_global"] = "false"
                    new_config["Core"]["memory_layout_mode\\default"] = "false"
                    new_config["Core"]["memory_layout_mode"] = layout
                    try:
                        with open(Setting_directory, "w") as config_file:
                            new_config.write(config_file, space_around_delimiters=False)
                    except Exception as e:
                        log.error(f"FAILED TO EDIT SETTINGS FILE: {e}")
            else:
                log.warning("Selected option has no associated setting folder.")

        def DownloadDFPS():
            DFPS_ver = self.DFPS_var.get()
            self.remove_list.append(DFPS_ver)
            link = DFPS_dict.get(DFPS_ver)
            Mod_directory = os.path.join(self.load_dir)
            if link is None:
                return
            if DFPS_ver == get_setting("dfps"):
                return
            if not DFPS_ver == "Latest":
                set_setting(args="dfps", value=DFPS_ver)
            self.progress_var.set(f"Downloading DFPS: {DFPS_ver}")
            log.info(f"Downloading DFPS: {DFPS_ver}")
            os.makedirs(Mod_directory, exist_ok=True)
            download_unzip(link, Mod_directory)
            log.info(f"Downloaded DFPS: {DFPS_ver}")

        def DownloadUI():
            log.info(f"starting the search for UI folder link.")
            new_list = []
            new_list.extend(UI_list)
            for item in AR_dict:
                new_list.append(item)

            if any(item in self.aspect_ratio_var.get().split(" ") for item in ["16-9", "16x9"]):
                log.info("Selected default Aspect Ratio.")
                if self.ui_var.get().lower() in ["none", "switch"]:
                    self.add_list.extend(new_list)
                    return
                new_folder = self.ui_var.get()
                link = UI_dict.get(new_folder)
            else:
                # define
                UIs = {
                    "PS4": ["ps", "ps4", "playstation", "ps5", "dualshock"],
                    "STEAMDECK": ["steamdeck", "deck"],
                    "XBOX": ["xbox", "xboxone"],
                }

                string_list = self.ui_var.get().lower().split(" ")

                for ui, tags in UIs.items():
                    if any(tag in string_list for tag in tags):
                        selected_ui = f" {ui} UI"
                        break
                    else:
                        selected_ui = ""

                # search
                new_folder = f"{self.aspect_ratio_var.get()}{selected_ui}"
                new_list.extend(UI_list)
                # fetch
                link = AR_dict.get(new_folder)

            # delete/disable
            new_list.remove(new_folder)
            self.add_list.extend(new_list)
            self.remove_list.append(new_folder)
            log.info(f"Attempting to download {new_folder}")
            self.progress_var.set(f"Downloading: {new_folder}\n(May take some time)")
            Mod_directory = os.path.join(self.load_dir)
            # skip
            if os.path.exists(os.path.join(Mod_directory, new_folder)):
                log.info(f"{new_folder} FOLDER already exists, continue...")
                return
            # download
            os.makedirs(Mod_directory, exist_ok=True)
            download_unzip(link, Mod_directory)
            log.info(f"Downloaded: {new_folder}")

        def DownloadFP():
            selected_fp_mod = self.fp_var.get()
            self.add_list.extend(FP_list)
            self.add_list.remove(selected_fp_mod)
            self.remove_list.append(selected_fp_mod)
            link = FP_dict.get(selected_fp_mod)
            Mod_directory = os.path.join(self.load_dir)
            full_dir = os.path.join(Mod_directory, selected_fp_mod)
            if link is None:
                return
            if os.path.exists(full_dir):
                return
            self.progress_var.set(f"Downloading: {selected_fp_mod}\n(May take some time)")
            log.info(f"Downloading: {selected_fp_mod}")
            os.makedirs(Mod_directory, exist_ok=True)
            download_unzip(link, Mod_directory)
            log.info(f"Downloaded: {selected_fp_mod}")

        def Disable_Mods():
            self.progress_var.set(f"Disabling old mods.")
            # Convert the lists to sets, removing any duplicates.
            self.add_list = set(self.add_list)
            self.remove_list = set(self.remove_list)
            # Run the Main code to Enable and Disable necessary Mods, the remove ensures the mods are enabled.
            if self.mode == "Yuzu":
                for item in self.add_list:
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, item, action="add")
                for item in self.remove_list:
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, item, action="remove")
            if self.mode == "Ryujinx":
                for item in self.add_list:
                    item_dir = os.path.join(self.load_dir, item)
                    if os.path.exists(item_dir):
                        shutil.rmtree(item_dir)
            self.add_list.clear()
            self.remove_list.clear()

        # Execute tasks and make a Progress Window.
        progress_window = Toplevel(self.window)
        progress_window.title("Downloading")
        window_width = 300
        window_height = 100
        screen_width = progress_window.winfo_screenwidth()
        screen_height = progress_window.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        progress_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        progress_window.resizable(False, False)
        total_iterations = 100
        self.progress_var = ttk.StringVar()
        self.progress_var.set("Applying the changes.")
        label = ttk.Label(progress_window, textvariable=self.progress_var)
        label.pack(pady=10)
        progress_bar = ttk.Progressbar(progress_window, mode="determinate", maximum=total_iterations)
        progress_bar.pack(pady=20)
        task_thread = threading.Thread(target=run_tasks)
        task_thread.start()