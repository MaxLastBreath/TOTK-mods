import threading
import webbrowser
import re
from configuration.settings import *
from configuration.settings_config import Setting
from modules.TOTK_Optimizer_Modules import * # imports all needed files.

class Manager:
    def __init__(self, window):
        # ULTRACAM 2.0 PATCHES ARE SAVED HERE.
        self.BEYOND_Patches = {}

        # Define the Manager window.
        self.window = window

        self.is_extracting = False

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
        self.mode = config.get("Mode", "managermode", fallback="Legacy")
        self.all_pages = ["main", "extra", "randomizer"]

        # Set neccesary variables.
        self.Curr_Benchmark = None
        self.Legacydir = None
        self.is_Ani_running = False
        self.is_Ani_Paused = False
        self.tooltip_active = False
        self.warn_again = "yes"
        self.title_id = title_id
        self.config_title_id = config_title_id
        self.old_cheats = {}
        self.cheat_version = ttk.StringVar(value="Version - 1.2.1")

        # Initialize Json Files.
        self.description = load_json("Description.json", descurl)
        self.presets = load_json("beyond_presets.json", presetsurl)
        self.version_options = load_json("Version.json", versionurl)
        self.cheat_options = load_json("Cheats.json", cheatsurl)
        self.ultracam_beyond = load_json("UltraCam_Template.json", ultracambeyond)
        self.Legacy_settings = load_json("Legacy_presets.json", Legacy_presets_url)

        self.benchmarks = {}

        if os.path.exists(os.path.join("UltraCam/UltraCam_Template.json")):
            with open("UltraCam/UltraCam_Template.json", "r", encoding="utf-8") as file:
                self.ultracam_beyond = json.load(file)

        # Local text variable
        self.switch_text = ttk.StringVar(value="Switch to Ryujinx")

        # Load Canvas
        Load_ImagePath(self)
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
        load_UI_elements(self, self.maincanvas)
        create_tab_buttons(self, self.maincanvas)

        # Create Text Position
        row = 40
        cul_tex = 60
        cul_sel = 220

        # Used for 2nd column.
        row_2 = 160
        cul_tex_2 = 400
        cul_sel_2 = 550

        def increase_row(row, cul_sel, cul_tex):
            row += 40
            if row >= 480:
                row = 160
                cul_tex += 180
                cul_sel += 180
            return row, cul_sel, cul_tex

        # Run Scripts for checking OS and finding location
        checkpath(self, self.mode)
        DetectOS(self, self.mode)

        # FOR DEBUGGING PURPOSES
        def onCanvasClick(event):
            print(f"CRODS = X={event.x} + Y={event.y} + {event.widget}")

        self.maincanvas.bind("<Button-3>", onCanvasClick)
        # Start of CANVAS options.

        # Create preset menu.
        presets = {"Saved": {}} | load_json("beyond_presets.json", presetsurl)
        values = list(presets.keys())
        self.selected_preset = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="OPTIMIZER PRESETS:",
                                                            variable=values[0], values=values,
                                                            row=row, cul=cul_tex - 20,
                                                            tags=["text"], tag="Optimizer",
                                                            description_name="Presets",
                                                            command=lambda event: apply_selected_preset(self)
                                                        )

        # Setting Preset - returns variable.

        value = ["No Change"]
        for item in self.Legacy_settings:
            value.append(item)
        self.selected_settings = self.on_canvas.create_combobox(
                                                            master=self.window, canvas=canvas,
                                                            text="Legacy SETTINGS:",
                                                            variable=value[0], values=value,
                                                            row=row, cul=340, drop_cul=480,
                                                            tags=["text"], tag="Legacy",
                                                            description_name="Settings"
                                                        )

        row += 40
        # Create a label for Legacy.exe selection
        backupbutton = cul_sel
        if self.os_platform == "Windows":
            command = lambda event: self.select_Legacy_exe()
            def browse():
                self.select_Legacy_exe()

            text = "SELECT EXECUTABLE"
            self.on_canvas.create_button(
                                        master=self.window, canvas=canvas,
                                        btn_text="Browse",
                                        row=row, cul=cul_sel, width=6,
                                        tags=["Button"],
                                        description_name="Browse",
                                        command=lambda: browse()
                                        )

            # Reset to Appdata
            def Legacy_appdata():
                checkpath(self, self.mode)
                log.info("Successfully Defaulted to Appdata!")
                save_user_choices(self, self.config, "appdata", None)

            self.on_canvas.create_button(
                                        master=self.window, canvas=canvas,
                                        btn_text="Use Appdata",
                                        row=row, cul=cul_sel + 68, width=9,
                                        tags=["Button"],
                                        description_name="Reset",
                                        command=Legacy_appdata
                                        )
            backupbutton = cul_sel + 165
        else:
            text = "Backup Save Files"
            command = None

        self.on_canvas.create_label(
                                    master=self.window, canvas=canvas,
                                    text=text,
                                    description_name="Browse",
                                    row=row, cul=cul_tex - 20,
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
                                    tags=["Button", "Legacy"],
                                    description_name="Shaders",
                                    command=lambda: clean_shaders(self)
        )
        row += 40

        # Create big TEXT label.
        #self.on_canvas.create_label(
        #                            master=self.window, canvas=canvas,
        #                            text="Graphics", font=bigfont, color=BigTextcolor,
        #                            description_name="Display Settings",
        #                            row=row, cul=cul_tex+100,
        #                            tags=["Big-Text"]
        #                            )

        self.graphics_element = self.on_canvas.Photo_Image(
            image_path="graphics.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        self.graphics_element_active = self.on_canvas.Photo_Image(
            image_path="graphics_active.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        self.extra_element = self.on_canvas.Photo_Image(
            image_path="extra.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        self.extra_element_active = self.on_canvas.Photo_Image(
            image_path="extra_active.png",
            width=int(70*1.6), height=int(48*1.6),
        )

        # Graphics & Extra & More - the -20 is extra
        self.on_canvas.image_Button(
            canvas=canvas,
            row=row - 35, cul=cul_tex - 10 - 20,
            img_1=self.graphics_element, img_2=self.graphics_element_active,
            command=lambda event: self.toggle_page(event, "main")
        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=row - 35, cul=cul_tex + 190 - 10,
            img_1=self.extra_element, img_2=self.extra_element_active,
            command=lambda event: self.toggle_page(event, "extra")
        )

        # BIG TEXT.
        self.on_canvas.create_label(
                                    master=self.window, canvas=canvas,
                                    text="Tears Of The Kingdom", font=bigfont, color=BigTextcolor,
                                    description_name="Mod Improvements", anchor="c",
                                    row=row, cul=575,
                                    tags=["Big-Text"]
                                    )

        row += 40

        ##              AUTO PATCH INFO STARTS HERE ALL CONTROLLED IN JSON FILE.
        ##              THIS IS FOR ULTRACAM BEYOND GRAPHICS AND PERFORMANCE (2.0)
        ##              REMOVED DFPS, SINCE ULTRACAM BEYOND DOES IT ALL AND SO MUCH BETTER.
        ##

        pos_dict = {
            "main": [row,  cul_tex, cul_sel, row_2, cul_tex_2, cul_sel_2],
            "extra": [row, cul_tex, cul_sel,  row_2, cul_tex_2, cul_sel_2]
        }

        keys = self.ultracam_beyond.get("Keys", [""])

        for name in keys:
            dicts = keys[name]

            patch_var = None
            patch_list = dicts.get("Name_Values", [""])
            patch_values = dicts.get("Values")
            patch_name = dicts.get("Name")
            patch_auto = dicts.get("Auto")
            section_auto = dicts.get("Section")
            patch_description = dicts.get("Description")
            patch_default_index = dicts.get("Default")
            pos = pos_dict[section_auto]
            if patch_auto is True:
                self.BEYOND_Patches[name] = tk.StringVar(master=self.window, value="auto")
                continue

            if dicts["Class"].lower() == "dropdown":
                patch_var = self.on_canvas.create_combobox(
                            master=self.window, canvas=canvas,
                            text=patch_name,
                            values=patch_list, variable=patch_list[patch_default_index],
                            row=pos[0], cul=pos[1], drop_cul=pos[2], width=100,
                            tags=["dropdown"], tag=section_auto,
                            text_description=patch_description
                            )
                new_pos = increase_row(pos[0], pos[1], pos[2])
                pos[0] = new_pos[0]
                pos[1] = new_pos[1]
                pos[2] = new_pos[2]

            if dicts["Class"].lower() == "scale":
                patch_type = dicts.get("Type")
                patch_increments = dicts.get("Increments")
                patch_var = self.on_canvas.create_scale(
                    master=self.window, canvas=canvas,
                    text=patch_name,
                    scale_from=patch_values[0], scale_to=patch_values[1], type=patch_type,
                    row=pos[0], cul=pos[1], drop_cul=pos[2], width=100, increments=float(patch_increments),
                    tags=["scale"], tag=section_auto,
                    text_description=patch_description
                )
                if patch_type == "f32":
                    print(f"{patch_name} - {patch_default_index}")
                    patch_var.set(float(patch_default_index))
                else:
                    patch_var.set(patch_default_index)

                canvas.itemconfig(patch_name, text=f"{float(patch_default_index)}")
                new_pos = increase_row(pos[0], pos[1], pos[2])
                pos[0] = new_pos[0]
                pos[1] = new_pos[1]
                pos[2] = new_pos[2]

            if dicts["Class"].lower() == "bool":
                patch_var = self.on_canvas.create_checkbutton(
                    master=self.window, canvas=canvas,
                    text=patch_name,
                    variable="Off",
                    row=pos[3], cul=pos[4], drop_cul=pos[5],
                    tags=["bool"], tag=section_auto,
                    text_description=patch_description
                )
                if patch_default_index:
                    patch_var.set("On")
                new_pos = increase_row(pos[3], pos[4], pos[5])
                pos[3] = new_pos[0]
                pos[4] = new_pos[1]
                pos[5] = new_pos[2]

            if patch_var is None:
                continue
            self.BEYOND_Patches[name] = patch_var

        row = pos_dict["main"][0]
        row_2 = pos_dict["main"][3]

        #for patch in self.BEYOND_Patches:
        #    log.info(f"{patch}: {self.BEYOND_Patches[patch].get()}")

        # Extra Patches. FP and Ui.
        self.fp_var = self.on_canvas.create_checkbutton(
                        master=self.window, canvas=canvas,
                        text="First Person",
                        variable="Off",
                        row=pos_dict["main"][3], cul=pos_dict["main"][4], drop_cul=pos_dict["main"][5],
                        tags=["bool"], tag="main",
                        description_name="First Person"
                )
        new_pos = increase_row(row_2, cul_sel_2, cul_tex_2)
        row_2 = new_pos[0]
        cul_sel_2 = new_pos[1]
        cul_tex_2 = new_pos[2]

        UI_list.remove("Black Screen Fix")
        self.ui_var = self.on_canvas.create_combobox(
                        master=self.window, canvas=canvas,
                        text="UI:",
                        variable=UI_list[0], values=UI_list,
                        row=row, cul=cul_tex, drop_cul=cul_sel,width=100,
                        tags=["text"], tag="main",
                        description_name="UI"
                                                    )
        row += 40

        # XYZ create patches, not used anymore though.
        #create_patches(self)

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

        self.extract_element = self.on_canvas.Photo_Image(
                        image_path="extract.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )
        self.extract_element_active = self.on_canvas.Photo_Image(
                        image_path="extract_active.png",
                        width=int(70*1.5), height=int(48*1.5),
                        )

        self.LOGO_element = self.on_canvas.Photo_Image(
                        image_path="optimizer_logo.png",
                        width=int(3316/10), height=int(823/10),
                        )

        self.LOGO_element_active = self.on_canvas.Photo_Image(
                        image_path="optimizer_logo_active.png",
                        width=int(3316/10), height=int(823/10),
                        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=510, cul=25,
            img_1=self.apply_element, img_2=self.apply_element_active,
            command=lambda event: self.submit()
        )

        # reverse scale.
        self.on_canvas.image_Button(
            canvas=canvas,
            row=510, cul=25 + int(self.apply_element.width() / sf),
            img_1=self.launch_element, img_2=self.launch_element_active,
            command=lambda event: launch_GAME(self)
        )

        # extract
        self.on_canvas.image_Button(
            canvas=canvas,
            row=510, cul=25 + int(7 + int(self.apply_element.width() / sf) * 2),
            img_1=self.extract_element, img_2=self.extract_element_active,
            command=lambda event: self.extract_patches()
        )

        self.on_canvas.image_Button(
            canvas=canvas,
            row=520, cul=850,
            img_1=self.LOGO_element, img_2=self.LOGO_element_active,
            command=lambda event: self.open_browser("Kofi")
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
        #        btn_text="Launch Game", tags=["Button", "Legacy"],
        #        row=530, cul=125, padding=10, width=9,
        #        description_name="Launch Game", style="warning.outline.TButton",
        #        command=lambda: launch_GAME(self)
        #    )

        # Load Saved User Options.
        self.toggle_page(0, "main")
        load_user_choices(self, self.config)
        return self.maincanvas

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
        create_tab_buttons(self, self.cheatcanvas)

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

    def select_Legacy_exe(self):
        if self.os_platform == "Windows":
            Legacy_path = filedialog.askopenfilename(
                title=f"Please select {self.mode}.exe",
                filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
            )
            executable_name = Legacy_path
            if executable_name.endswith("Ryujinx.exe") or executable_name.endswith("Ryujinx.Ava.exe"):
                if self.mode == "Legacy":
                    self.switchmode("true")
            else:
                if self.mode == "Ryujinx":
                    self.switchmode("true")

            if Legacy_path:
                # Save the selected Legacy.exe path to a configuration file
                save_user_choices(self, self.config, Legacy_path)
                home_directory = os.path.dirname(Legacy_path)
                fullpath = os.path.dirname(Legacy_path)
                if any(item in os.listdir(fullpath) for item in ["user", "portable"]):
                    log.info(
                        f"Successfully selected {self.mode}.exe! And a portable folder was found at {home_directory}!")
                    checkpath(self, self.mode)
                    return Legacy_path
                else:
                    log.info(f"Portable folder for {self.mode} not found defaulting to appdata directory!")
                    checkpath(self, self.mode)
                    return Legacy_path

                # Update the Legacy.exe path in the current session
                self.Legacy_path = Legacy_path
            else:
                checkpath(self, self.mode)
                return None
            # Save the selected Legacy.exe path to a configuration file
            save_user_choices(self, self.config, Legacy_path)
        return Legacy_path

    def show_main_canvas(self):
        self.on_canvas.is_Ani_Paused = True
        self.cheatcanvas.pack_forget()
        self.maincanvas.pack()

    def toggle_page(self, event, show):
        self.maincanvas.itemconfig(show, state="normal")
        log.info(show)
        for state in self.all_pages:
            if state is not show:
                self.maincanvas.itemconfig(state, state="hidden")

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
        load_benchmark(self)

    def Cheat_UI_elements(self, canvas):
        self.cheatbg = canvas.create_image(0, -scale(300), anchor="nw", image=self.blurbackground, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_LegacyBG, tags="overlay-1")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI_Cheats, tags="overlay")

    def switchmode(self, command="true"):
        if command == "true":
            if self.mode == "Legacy":
                self.mode = "Ryujinx"
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="hidden")
                self.switch_text.set("Switch to Legacy")
                return
            elif self.mode == "Ryujinx":
                self.mode = "Legacy"
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_LegacyBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="normal")
                # change text
                self.switch_text.set("Switch to Ryujinx")
                return
        elif command == "false":
            if self.mode == "Ryujinx":
                for canvas in self.all_canvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="hidden")
                self.switch_text.set("Switch to Legacy")
                return
        elif command == "Mode":
            return self.mode

    def fetch_var(self, var, dict, option):
        if not dict.get(option, "") == "":
            var.set(dict.get(option, ""))
        return

    # Submit the results, run download manager. Open a Loading screen.

    def extract_patches(self):
        self.is_extracting = True
        checkpath(self, self.mode)
        self.submit()

    def submit(self, mode=None):
        self.add_list = []
        self.remove_list = []
        checkpath(self, self.mode)
        # Needs to be run after checkpath.
        if self.mode == "Legacy":
            qtconfig = get_config_parser()
            qtconfig.optionxform = lambda option: option
            try:
                qtconfig.read(self.configdir)
            except Exception as e: log.warning(f"Couldn't' find QT-config {e}")
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
                def stop_extracting():
                    self.is_extracting = False

                tasklist = [Exe_Running(), DownloadBEYOND(), DownloadUI(), DownloadFP(), UpdateSettings(), Create_Mod_Patch(), Disable_Mods(), stop_extracting()]
                if get_setting("auto-backup") in ["On"]:
                    tasklist.append(backup(self))
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                progress_window.destroy()

                m = 1.3
                # Kofi button.
                element_1 = self.on_canvas.Photo_Image(
                    image_path="support.png",
                    width=int(70* m), height=int(48* m),
                )

                element_2 = self.on_canvas.Photo_Image(
                    image_path="support_active.png",
                    width=int(70* m), height=int(48* m),
                )

                element_3 = self.on_canvas.Photo_Image(
                    image_path="no_thanks.png",
                    width=int(70* m), height=int(48* m),
                )

                element_4 = self.on_canvas.Photo_Image(
                    image_path="no_thanks_active.png",
                    width=int(70* m), height=int(48* m),
                )

                if not self.os_platform == "Linux":
                    dialog = CustomDialog(self, "TOTK Optimizer Tasks Completed",
                                          "",
                                          yes_img_1=element_1,
                                          yes_img_2=element_2,
                                          no_img_1=element_3,
                                          no_img_2=element_4,
                                          custom_no="No Thanks",
                                          width=384,
                                          height=216
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
                # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Legacy together.
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
                log.info(f"Generating mod at {self.load_dir}")
                os.makedirs(self.load_dir, exist_ok=True)

                # Update progress bar
                self.progress_var.set("TOTK Optimizer Patch.")

                # Ensures that the patches are active and ensure that old versions of the mod folder is disabled.
                self.remove_list.append("!!!TOTK Optimizer")
                self.add_list.append("Visual Improvements")
                self.add_list.append("Mod Manager Patch")
                self.add_list.append("UltraCam")

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
                    if self.BEYOND_Patches[patch] == "auto" or self.BEYOND_Patches[patch].get() == "auto":
                        if patch_class.lower() == "dropdown":
                            patch_Names = patch_dict["Name_Values"]
                            config[patch_Config[0]][patch_Config[1]] = str(patch_Names[patch_Default])
                        else:
                            config[patch_Config[0]][patch_Config[1]] = str(patch_Default)
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
                if(new_scale > 1):
                    layout = 1
                if(new_scale > 6):
                    layout = 2

                if self.mode == "Legacy":
                    write_Legacy_config(self, self.TOTKconfig, self.title_id, "Renderer", "resolution_setup", "2")
                    write_Legacy_config(self, self.TOTKconfig, self.title_id, "Core", "memory_layout_mode", f"{layout}")
                    write_Legacy_config(self, self.TOTKconfig, self.title_id, "System", "use_docked_mode", "true")

                    if layout > 0:
                        write_Legacy_config(self, self.TOTKconfig, self.title_id, "Renderer", "vram_usage_mode", "1")
                    else:
                        write_Legacy_config(self, self.TOTKconfig, self.title_id, "Renderer", "vram_usage_mode", "0")

                if self.mode == "Ryujinx":
                    write_ryujinx_config(self, self.ryujinx_config, "res_scale", 1)
                    if (layout > 0):
                        write_ryujinx_config(self, self.ryujinx_config, "expand_ram", True)
                    else:
                        write_ryujinx_config(self, self.ryujinx_config, "expand_ram", False)

                config["Resolution"]["Width"] = str(New_Resolution[0])
                config["Resolution"]["Height"] = str(New_Resolution[1])

                ## WRITE IN CONFIG FILE FOR UC 2.0
                with open(ini_file_path, 'w+', encoding="utf-8") as configfile:
                    config.write(configfile)


            # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Legacy together.
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
            log.info("Checking for Settings...")
            self.progress_var.set("Creating Settings..")
            if self.selected_settings.get() == "No Change":
                self.progress_var.set("No Settings Required..")
                return
            if self.mode == "Legacy":
                setting_preset = self.Legacy_settings[self.selected_settings.get()]
                for section in setting_preset:
                    for option in setting_preset[section]:
                        write_Legacy_config(self, self.TOTKconfig, self.title_id, section, option, str(setting_preset[section][option]))
            self.progress_var.set("Finished Creating Settings..")

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
                if os.path.exists("TOTKOptimizer/exefs"):
                    log.info("Found a local UltraCam Folder. COPYING to !!!TOTK Optimizer.")
                    if os.path.exists(os.path.join(Mod_directory, "exefs")):
                        shutil.rmtree(os.path.join(Mod_directory, "exefs"))
                    shutil.copytree(os.path.join("TOTKOptimizer/exefs"), os.path.join(Mod_directory, "exefs"))
                    log.info("\n\nEARLY ACCESS ULTRACAM APPLIED\n\n.")
                    return

                self.progress_var.set(f"Downloading UltraCam BEYOND")
                log.info(f"Downloading: UltraCam")
                os.makedirs(Mod_directory, exist_ok=True)
                download_unzip(link, Mod_directory)
                log.info(f"Downloaded: UltraCam")
            except Exception as e:
                log.warning(f"FAILED TO DOWNLOAD ULTRACAM BEYOND! {e}")

        def DownloadUI():
            selected_ui = "NONE"
            log.info(f"starting the search for UI folder link.")
            new_list = []
            new_list.extend(UI_list)
            for item in AR_dict:
                new_list.append(item)

            if self.BEYOND_Patches["aspect ratio"].get() in ["16-9", "16x9"]:
                log.info("Selected default Aspect Ratio.")
                if self.ui_var.get().lower() in ["none", "switch"]:
                    self.add_list.extend(new_list)
                new_folder = self.ui_var.get()
                link = UI_dict.get(new_folder)
            else:
                # define
                UIs = {
                    "PS4": ["ps", "ps4", "playstation", "ps5", "dualshock"],
                    "STEAMDECK": ["steamdeck", "deck"],
                    "XBOX": ["xbox", "xboxone"],
                }
                string = self.ui_var.get().lower().split(" ")[0]
                log.info(string)
                for ui, tags in UIs.items():
                    if string in tags:
                        selected_ui = f" {ui} UI"

                # search
                new_folder = f"Aspect Ratio {self.BEYOND_Patches['aspect ratio'].get().replace('x', '-')}{selected_ui}"
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

            Mod_directory = os.path.join(self.load_dir, "!!!TOTK Optimizer")
            if selected_fp_mod.lower() == "on":
                link = FP_Mod
                self.progress_var.set(f"Downloading: {selected_fp_mod}\n(May take some time)")
                log.info(f"Downloading: {selected_fp_mod}")
                os.makedirs(Mod_directory, exist_ok=True)
                download_unzip(link, Mod_directory)
                log.info(f"Downloaded: {selected_fp_mod}")

            fp_dir = os.path.join(Mod_directory, "romfs", "Pack", "Actor", "PlayerCamera.pack.zs")
            if selected_fp_mod.lower() == "off" and os.path.exists(fp_dir):
                os.remove(fp_dir)

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
            if self.mode == "Legacy":
                for item in self.add_list:
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.config_title_id, item, action="add")
                for item in self.remove_list:
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.config_title_id, item, action="remove")
            if self.mode == "Ryujinx" or platform.system() == "Linux" and not self.is_extracting:
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