import threading
import tkinter
import ttkbootstrap as ttk
import webbrowser
import re
from tkinter import filedialog, Toplevel
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from modules.canvas import *
from modules.qt_config import modify_disabled_key, get_config_parser
from modules.checkpath import checkpath, DetectOS
from modules.backup import *
from modules.logger import *
from modules.launch import *
from modules.config import *
from modules.util import *
from configuration.settings import *
from configuration.settings_config import Setting

class Manager:
    def __init__(self, window):
        # ULTRACAM 2.0 PATCHES ARE SAVED HERE.
        self.BEYOND_Patches = {}


        # Define the Manager window.
        self.window = window

        self.DFPS_var = "BEYOND"

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
        self.ultracam_options = load_json("UltraCam.json", ultracam)
        self.ultracam_beyond = load_json("UltraCam_Template.json", ultracambeyond)

        if os.path.exists(os.path.join("UltraCam/UltraCam_Template.json")):
            with open("UltraCam/UltraCam_Template.json", "r") as file:
                self.ultracam_beyond = json.load(file)

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

        self.selected_options = {}

        # Load UI Elements
        self.load_UI_elements(self.maincanvas)
        self.create_tab_buttons(self.maincanvas)

        # Create Text Position
        row = 40
        cul_tex = 40
        cul_sel = 200

        # Used for 2nd column.
        self.row_2 = 120
        self.cul_tex_2 = 400
        self.cul_sel_2 = 550

        def increase_row_2():
            self.row_2 += 40
            if self.row_2 >= 480:
                self.row_2 = 120
                self.cul_tex_2 += 180
                self.cul_sel_2 += 180


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
                                                            text="OPTIMIZER PRESETS:",
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
                                                            text="YUZU SETTINGS:",
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
                                        tags=["Button"],
                                        description_name="Reset",
                                        command=yuzu_appdata
                                        )
            backupbutton = cul_sel + 165
            text = "SELECT Yuzu.exe"
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
                                    tags=["Button"],
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
                                    text="Graphics", font=bigfont, color=BigTextcolor,
                                    description_name="Display Settings",
                                    row=row, cul=cul_tex+100,
                                    tags=["Big-Text"]
                                    )

        self.on_canvas.create_label(
                                    master=self.window, canvas=canvas,
                                    text="Tweaks & More", font=bigfont, color=BigTextcolor,
                                    description_name="Mod Improvements",
                                    row=row, cul=400+100,
                                    tags=["Big-Text"]
                                    )

        row += 40

        ##              AUTO PATCH INFO STARTS HERE ALL CONTROLLED IN JSON FILE.
        ##              THIS IS FOR ULTRACAM BEYOND GRAPHICS AND PERFORMANCE (2.0)
        ##              REMOVED DFPS, SINCE ULTRACAM BEYOND DOES IT ALL AND SO MUCH BETTER.
        ##
        ##
        ##

        keys = self.ultracam_beyond.get("Keys", [""])

        for name in keys:
            dicts = keys[name]

            patch_var = None
            patch_list = dicts.get("Name_Values", [""])
            patch_values = dicts.get("Values")
            patch_name = dicts.get("Name")
            patch_auto = dicts.get("Auto")
            patch_description = dicts.get("Description")
            patch_default_index = dicts.get("Default")
            if patch_auto is True:
                self.BEYOND_Patches[name] = "auto"
                continue
            if dicts["Class"].lower() == "dropdown":
                patch_var = self.on_canvas.create_combobox(
                            master=self.window, canvas=canvas,
                            text=patch_name,
                            values=patch_list, variable=patch_list[patch_default_index],
                            row=row, cul=cul_tex, drop_cul=cul_sel, width=100,
                            tags=["dropdown"], tag="UltraCam",
                            text_description=patch_description
                            )
                log.info(patch_var.get())
                row += 40

            if dicts["Class"].lower() == "scale":
                patch_var = self.on_canvas.create_scale(
                    master=self.window, canvas=canvas,
                    text=patch_name,
                    scale_from=patch_values[0], scale_to=patch_values[1],
                    row=row, cul=cul_tex, drop_cul=cul_sel, width=100,
                    tags=["scale"], tag="UltraCam",
                    text_description=patch_description
                )
                patch_var.set(patch_default_index)
                canvas.itemconfig(patch_name, text=f"{patch_default_index}")
                log.info(patch_var.get())
                row += 40

            if dicts["Class"].lower() == "bool":
                patch_var = self.on_canvas.create_checkbutton(
                    master=self.window, canvas=canvas,
                    text=patch_name,
                    variable="Off",
                    row=self.row_2 + 40, cul=self.cul_tex_2, drop_cul=self.cul_sel_2,
                    tags=["bool"], tag="UltraCam",
                    text_description=patch_description
                )
                if patch_default_index:
                    patch_var.set("On")
                increase_row_2()

            if patch_var is None:
                continue
            self.BEYOND_Patches[name] = patch_var


        for patch in self.BEYOND_Patches:
            log.info(f"{patch}: {self.BEYOND_Patches[patch].get()}")

        # Extra Patches. FP and Ui.
        self.fp_var = self.on_canvas.create_checkbutton(
                        master=self.window, canvas=canvas,
                        text="First Person",
                        variable="Off",
                        row=self.row_2 + 40, cul=self.cul_tex_2, drop_cul=self.cul_sel_2,
                        tags=["bool"], tag="External",
                        description_name="First Person"
                )
        increase_row_2()

        self.ui_var = self.on_canvas.create_combobox(
                        master=self.window, canvas=canvas,
                        text="UI:",
                        variable=UI_list[0], values=UI_list,
                        row=row, cul=cul_tex, drop_cul=cul_sel,width=100,
                        tags=["text"], tag=None,
                        description_name="UI"
                                                    )
        row += 40


        # XYZ create patches, not used anymore though.
        #self.create_patches()

        self.apply_element = self.on_canvas.Photo_Image(
                        image_path="apply.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.apply_element_active = self.on_canvas.Photo_Image(
                        image_path="apply_active.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.launch_element = self.on_canvas.Photo_Image(
                        image_path="launch.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )
        self.launch_element_active = self.on_canvas.Photo_Image(
                        image_path="launch_active.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=510, cul=25,
            img_1=self.apply_element, img_2=self.apply_element_active,
            command=lambda event: self.submit()
        )
        if self.os_platform == "Windows":
            # reverse scale.
            self.on_canvas.image_Button(
                canvas=canvas,
                row=510, cul=25 + int(self.apply_element.width() / sf),
                img_1=self.launch_element, img_2=self.launch_element_active,
                command=lambda event: launch_GAME(self)
            )

        # Create a submit button
        #self.on_canvas.create_button(
        #    master=self.window, canvas=canvas,
        #    btn_text="APPLY", tags=["Button"],
        #    row=530, cul=25, padding=10, width=9,
        #    description_name="Apply", style="warning",
        #    command=self.submit
        #)

        #if self.os_platform == "Windows":
        #    # Create a submit button
        #    self.on_canvas.create_button(
        #        master=self.window, canvas=canvas,
        #        btn_text="Launch Game", tags=["Button", "Yuzu"],
        #        row=530, cul=125, padding=10, width=9,
        #        description_name="Launch Game", style="warning.outline.TButton",
        #        command=lambda: launch_GAME(self)
        #    )

        # Load Saved User Options.
        load_user_choices(self, self.config)
        return self.maincanvas

    def create_patches(self, row = 120, cul_tex= 400, cul_sel = 550):
        versionvalues = []

        try:
            for key_var, value in self.selected_options.items():
                value = value.get()
                self.old_patches[key_var] = value
        except AttributeError as e:
            self.old_patches = {}

        # Delete the patches before making new ones.
        self.maincanvas.delete("patches")
        # Make UltraCam Patches First.

        UltraCam_Option = "Improve Fog"
        self.fog_var = self.on_canvas.create_checkbutton(
                master=self.window, canvas=self.maincanvas,
                text=UltraCam_Option,
                variable="Off",
                row=row + 40, cul=cul_tex, drop_cul=cul_sel,
                tags=["text"], tag="patches",
                description_name="Improve Fog"
        )

        self.selected_options[UltraCam_Option] = self.fog_var
        try:
            if self.old_patches.get(UltraCam_Option) == "On" and not self.old_patches == {}:
                self.fog_var.set("On")
        except AttributeError as e:
            self.old_patches = {}
        row += 40

        # Create labels and enable/disable options for each entry
        for version_option_name, version_option_value in self.version_options[0].items():

            # Create label
            if version_option_name not in ["Source", "nsobid", "offset", "version"]:

                if self.DFPS_var == "UltraCam" and version_option_name in self.ultracam_options.get(
                        "Skip_Patches"):
                    continue

                # Create checkbox
                version_option_var = self.on_canvas.create_checkbutton(
                    master=self.window, canvas=self.maincanvas,
                    text=version_option_name,
                    variable="Off",
                    row=row + 40, cul=cul_tex, drop_cul=cul_sel,
                    tags=["text"], tag="patches",
                    description_name=version_option_name
                )
                self.selected_options[version_option_name] = version_option_var


                try:
                    if self.old_patches.get(version_option_name) == "On" and not self.old_patches == {}:
                        version_option_var.set("On")
                except AttributeError as e:
                    self.old_patches = {}

                # Increase +40 space for each patch.
                row += 40

            if row >= 480:
                row = 20
                cul_tex += 180
                cul_sel += 180

    def update_scaling_variable(self, something=None):
        if self.DFPS_var == "UltraCam":
            self.fps_var.set(self.fps_var_new.get())

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

        self.background_UI_Cheats = self.on_canvas.Photo_Image(
            image_path="BG_Left_Cheats.png",
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
            blur=2
        )

        if os.path.exists("custom/cbg.jpg"):
            image_path = "custom/cbg.jpg"
        elif os.path.exists("custom/cbg.png"):
            image_path = "custom/cbg.png"
        else:
            image_path = "image_cheats.png"

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
            img_1=self.master_sword_element, img_2=self.master_sword_element_active, effect_folder="effect1",
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
        #text_widgetoutline2 = canvas.create_text(scale(1001) - scale(20), scale(126) -scale(80), text=f"{self.mode} TOTK Optimizer", tags="information", fill="black", font=biggyfont, anchor="center", justify="center", width=scale(325))
        #text_widget2 = canvas.create_text(scale(1000)-scale(20), scale(126)-scale(80), text=f"{self.mode} TOTK Optimizer", tags="information", fill="#FBF8F3", font=biggyfont, anchor="center", justify="center", width=scale(325))

        text_widgetoutline1 = canvas.create_text(scale(1001) -scale(20) -scale(10), scale(126) + scale(10), text=self.text_content, fill="black", font=biggyfont, anchor="center", justify="center", width=scale(325))
        text_widget1 = canvas.create_text(scale(1000) - scale(20) -scale(10), scale(125) +scale(10), text=self.text_content, fill="#FBF8F3", font=biggyfont, anchor="center", justify="center", width=scale(325))

    def Cheat_UI_elements(self, canvas):
        self.cheatbg = canvas.create_image(0, -scale(300), anchor="nw", image=self.blurbackground, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_YuzuBG, tags="overlay-1")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI_Cheats, tags="overlay")

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
                    canvas.itemconfig("Select-EXE", text=f"SELECT Ryujinx.exe")
                    canvas.itemconfig("yuzu", state="hidden")
                self.switch_text.set("Switch to Yuzu")
                return
            elif self.mode == "Ryujinx":
                self.mode = "Yuzu"
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_YuzuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Select-EXE", text=f"SELECT Yuzu.exe")
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

        if selected_preset == "Saved":
            load_user_choices(self, self.config)

        elif selected_preset in self.presets:
            preset_to_apply = self.presets[selected_preset]
            for key, value in preset_to_apply.items():
                if value.lower() in ["enable", "enabled", "on"]:
                    preset_to_apply[key] = "On"
                elif value.lower() in ["disable", "disabled", "off"]:
                    preset_to_apply[key] = "Off"
            # Apply the selected preset from the online presets
            self.apply_preset(self.presets[selected_preset])
    def fetch_var(self, var, dict, option):
        if not dict.get(option, "") == "":
            var.set(dict.get(option, ""))
        return

    def apply_preset(self, preset_options):
        self.fetch_var(self.resolution_var, preset_options, "Resolution")
        self.fetch_var(self.fps_var, preset_options, "FPS")
        self.fetch_var(self.ui_var, preset_options, "UI")
        self.fetch_var(self.aspect_ratio_var, preset_options, "Aspect Ratio")
        self.fetch_var(self.fp_var, preset_options, "First Person")
        self.fetch_var(self.selected_settings, preset_options, "Settings")

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
                title=f"Please select {self.mode}.exe",
                filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
            )
            executable_name = yuzu_path
            if executable_name.endswith("Ryujinx.exe") or executable_name.endswith("Ryujinx.Ava.exe"):
                if self.mode == "Yuzu":
                    self.switchmode("true")
            if executable_name.endswith("yuzu.exe"):
                if self.mode == "Ryujinx":
                    self.switchmode("true")
            if yuzu_path:
                # Save the selected yuzu.exe path to a configuration file
                save_user_choices(self, self.config, yuzu_path)
                home_directory = os.path.dirname(yuzu_path)
                fullpath = os.path.dirname(yuzu_path)
                if any(item in os.listdir(fullpath) for item in ["user", "portable"]):
                    log.info(f"Successfully selected {self.mode}.exe! And a portable folder was found at {home_directory}!")
                    checkpath(self, self.mode)
                    return yuzu_path
                else:
                    log.info(f"Portable folder for {self.mode} not found defaulting to appdata directory!")
                    checkpath(self, self.mode)
                    return yuzu_path

                # Update the yuzu.exe path in the current session
                self.yuzu_path = yuzu_path
            else:
                checkpath(self, self.mode)
                return None
            # Save the selected yuzu.exe path to a configuration file
            save_user_choices(self, self.config, yuzu_path)
        return yuzu_path
    # Load Yuzu Dir
    def load_yuzu_path(self, config_file):
        if self.mode == "Yuzu":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            yuzu_path = config.get('Paths', 'yuzupath', fallback="Appdata")
            return yuzu_path
        if self.mode == "Ryujinx":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            ryujinx_path = config.get('Paths', 'ryujinxpath', fallback="Appdata")
            return ryujinx_path

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

        def mod_list(arg, mod):
            try:
                if arg in ["r", "remove"]:
                    self.add_list.remove(mod)
                if arg in ["a", "add"]:
                    self.remove_list.append(mod)
            except Exception as e:
                log.warning(print(f"The Mod: {mod}, doesn't exist anymore,"
                                  f"\nconsider changing it to a different one."))
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
                log.info("Tasks have been COMPLETED. Feel free to Launch the game.")
                return
            if mode== None:
                log.info("Starting TASKs for Normal Patch..")
                tasklist = [Exe_Running(), DownloadFP(), DownloadUI(), DownloadBEYOND(), UpdateSettings(), Create_Mod_Patch(), Disable_Mods()]
                if get_setting("auto-backup") in ["On"]:
                    tasklist.append(backup(self))
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                progress_window.destroy()
                message = (f"MODS HAVE BEEN APPLIED!\n"
                           f"If you like TOTK Optimizer\n"
                           f"And the UltraCam Mod.\n"
                           f"Feel free to check out my Kofi.\n"
                           )
                # Kofi button.
                element_1 = self.on_canvas.Photo_Image(
                    image_path="support.png",
                    width=70, height=48,
                )

                element_2 = self.on_canvas.Photo_Image(
                    image_path="support_active.png",
                    width=70, height=48,
                )

                element_3 = self.on_canvas.Photo_Image(
                    image_path="no_thanks.png",
                    width=70, height=48,
                )

                element_4 = self.on_canvas.Photo_Image(
                    image_path="no_thanks_active.png",
                    width=70, height=48,
                )

                if not self.os_platform == "Linux":
                    dialog = CustomDialog(self, "TOTK Optimizer Tasks Completed",
                                          message,
                                          yes_img_1=element_1,
                                          yes_img_2=element_2,
                                          no_img_1=element_3,
                                          no_img_2=element_4,
                                          custom_no="No Thanks",
                                          width=300,
                                          height=200
                                          )
                    dialog.wait_window()
                    if dialog.result:
                        self.open_browser("kofi")

                log.info("Tasks have been COMPLETED. Feel free to Launch the game.")
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
                        with open(filename, "w", encoding="utf-8") as file:
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

                # Ensures that the patches are active and ensure that old versions of the mod folder is disabled.
                self.remove_list.extend(["!!!TOTK Optimizer"])
                self.add_list.append("Visual Improvements")
                self.add_list.append("Mod Manager Patch")


                ini_file_directory = os.path.join(self.load_dir, "!!!TOTK Optimizer", "romfs", "UltraCam")
                os.makedirs(ini_file_directory, exist_ok=True)
                ini_file_path = os.path.join(ini_file_directory, "maxlastbreath.ini")

                config = configparser.ConfigParser()
                config.optionxform = lambda option: option
                if os.path.exists(ini_file_path):
                    config.read(ini_file_path)


                ## TOTK UC BEYOND AUTO PATCHER
                patch_info = self.ultracam_beyond.get("Keys", [""])
                for patch in self.BEYOND_Patches:
                    if patch.lower() in ["resolution", "aspect ratio"]:
                        continue

                    patch_dict = patch_info[patch]
                    patch_class = patch_dict["Class"]
                    patch_Config = patch_dict["Config_Class"]
                    patch_Default = patch_dict["Default"]

                    # Ensure we have the section required.
                    if not config.has_section(patch_Config[0]):
                        config[patch_Config[0]] = {}

                    # In case we have an auto patch.
                    if self.BEYOND_Patches[patch] == "auto":
                        config[patch_Config[0]][patch_Config[1]] = patch_Default
                        continue

                    if patch_class.lower() == "bool" or patch_class.lower() == "scale":
                        config[patch_Config[0]][patch_Config[1]] = self.BEYOND_Patches[patch].get()

                    if patch_class.lower() == "dropdown":
                        # exclusive to dropdown.
                        patch_Names = patch_dict["Name_Values"]
                        patch_Values = patch_dict["Values"]
                        index = patch_Names.index(self.BEYOND_Patches[patch].get())
                        config[patch_Config[0]][patch_Config[1]] = str(patch_Values[index])

                resolution = self.BEYOND_Patches["resolution"].get()
                shadows = int(self.BEYOND_Patches["shadow resolution"].get().split("x")[0])

                ARR = self.BEYOND_Patches["aspect ratio"].get().split("x")
                New_Resolution = patch_info["resolution"]["Values"][patch_info["resolution"]["Name_Values"].index(resolution)].split("x")
                New_Resolution = convert_resolution(int(New_Resolution[0]), int(New_Resolution[1]), int(ARR[0]), int(ARR[1]))

                scale_1080 = 1920*1080
                scale_shadows = round(shadows / 1024)
                New_Resolution_scale = int(New_Resolution[0]) * int(New_Resolution[1])
                new_scale = New_Resolution_scale / scale_1080

                if (scale_shadows > new_scale):
                    new_scale = scale_shadows
                    log.info(f"scale:{new_scale}")

                layout = 0
                if(new_scale < 0):
                    layout = 0
                if(new_scale > 2):
                    layout = 1
                if(new_scale > 6):
                    layout = 2

                if self.mode == "Yuzu":
                    write_yuzu_config(self.TOTKconfig, "Renderer", "resolution_setup", "1")
                    write_yuzu_config(self.TOTKconfig, "Core", "memory_layout_mode", f"{layout}")

                if self.mode == "Ryujinx":
                    write_ryujinx_config(self.ryujinx_config, "res_scale", 1)

                config["Resolution"]["Width"] = str(New_Resolution[0])
                config["Resolution"]["Height"] = str(New_Resolution[1])



                ## WRITE IN CONFIG FILE FOR UC 2.0
                with open(ini_file_path, 'w', encoding="utf-8") as configfile:
                    config.write(configfile)


            # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Yuzu together.
            try:
                # This logic is disabled with UltraCam Beyond.
                if self.DFPS_var == "BEYOND":
                    log.info("FINISHED APPLYING PATCHES")
                    return

                for version_option in self.version_options:
                    version = version_option.get("version", "")
                    mod_path = os.path.join(self.load_dir, "Mod Manager Patch", "exefs")

                    # Create the directory if it doesn't exist
                    os.makedirs(mod_path, exist_ok=True)

                    filename = os.path.join(mod_path, f"{version}.pchtxt")
                    all_values = []
                    with open(filename, "w", encoding="utf-8") as file:
                        file.write(version_option.get("Source", "") + "\n")
                        file.write(version_option.get("nsobid", "") + "\n")
                        file.write(version_option.get("offset", "") + "\n")
                        for key, value in version_option.items():
                            if self.DFPS_var == "UltraCam" and key in self.ultracam_options.get(
                                    "Skip_Patches"):
                                continue

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
            except PermissionError as e:
                log.error(f"FAILED TO CREATE MOD PATCH: {e}")

        def UpdateSettings():
            if self.mode == "Ryujinx":
                print("Ryujinx Doesn't support custom settings as it, doesn't require them.")
                return
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
                    else:
                        log.error(f"Failed to download file from {raw_url}. Status code: {response.status_code}")
                        return
            else:
                log.warning("Selected option has no associated setting folder.")

        def DownloadBEYOND():
            try:
                self.add_list.append("UltraCam")
                self.add_list.append("Max DFPS++")
                self.add_list.append("DFPS")
                link = New_UCBeyond_Download

                Mod_directory = os.path.join(self.load_dir, "!!!TOTK Optimizer")
                if link is None:
                    log.critical("Couldn't find a link to DFPS/UltraCam")
                    return
                set_setting(args="dfps", value="UltraCam")

                # Apply UltraCam from local folder.
                if os.path.exists("UltraCam/exefs"):
                    log.info("Found a local UltraCam Folder. COPYING to !!!TOTK Optimizer.")
                    if os.path.exists(os.path.join(Mod_directory, "exefs")):
                        shutil.rmtree(os.path.join(Mod_directory, "exefs"))
                    shutil.copytree(os.path.join("UltraCam/exefs"), os.path.join(Mod_directory, "exefs"))
                    log.info("Applied New UltraCam.")
                    return

                self.progress_var.set(f"Downloading UltraCam BEYOND")
                log.info(f"Downloading: UltraCam")
                os.makedirs(Mod_directory, exist_ok=True)
                download_unzip(link, Mod_directory)
                log.info(f"Downloaded: UltraCam")
            except Exception as e:
                log.warning(f"FAILED TO DOWNLOAD ULTRACAM BEYOND! {e}")

        def DownloadUI():
            log.info(f"starting the search for UI folder link.")
            new_list = []
            new_list.extend(UI_list)
            for item in AR_dict:
                new_list.append(item)

            if any(item in self.ultracam_beyond.get("Keys") for item in ["16-9", "16x9"]):
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
                new_folder = f"{self.BEYOND_Patches['aspect ratio']}{selected_ui}"
                new_list.extend(UI_list)
                # fetch
                link = AR_dict.get(new_folder)

            # delete/disable
            try:
                new_list.remove(new_folder)
            except Exception as e:
                log.warning(print(f"The Mod: {new_folder}, doesn't exist anymore,"
                                  f"\nconsider changing it to a different one."))
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
            mod_list("a", selected_fp_mod)
            mod_list("r", selected_fp_mod)
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

        def Exe_Running():
            is_Program_Opened = is_process_running(self.mode + ".exe")
            message = (f"{self.mode}.exe is Running, \n"
                       f"The Optimizer Requires {self.mode}.exe to be closed."
                       f"\nDo you wish to close {self.mode}.exe?")
            if is_Program_Opened is True:
                response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)
                if response is True:
                    subprocess.run(["taskkill", "/F", "/IM", f"{self.mode}.exe"], check=True)
            if is_Program_Opened is False:
                log.info(f"{self.mode}.exe is closed, working as expected.")

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
            if self.mode == "Ryujinx" or platform.system() == "Linux":
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
