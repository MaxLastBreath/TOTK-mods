from configuration.settings import *
from configuration.settings_config import Setting
from modules.TOTK_Optimizer_Modules import *  # imports all needed files.
from modules.GameManager.GameManager import Game_Manager
from modules.GameManager.PatchInfo import PatchInfo
from modules.GameManager.FileManager import FileManager
from modules.GameManager.LaunchManager import LaunchManager
from modules.FrontEnd.TextureMgr import TextureMgr
from modules.load_elements import create_tab_buttons, load_UI_elements
import threading, webbrowser, os, copy
import ttkbootstrap as ttk


def increase_row(row, cul_sel, cul_tex):
    row += 40
    if row >= 480:
        row = 160
        cul_tex += 180
        cul_sel += 180
    return row, cul_sel, cul_tex


class Manager:
    patches: list[PatchInfo] = []
    all_canvas: list[ttk.Canvas] = []
    PageBtns: list[ImageButton] = []

    old_cheats: dict = {}
    benchmarks: dict = {}

    _patchInfo: PatchInfo = None
    _window: ttk.Window
    constyle: ttk.Style
    os_platform: str = platform.system()

    Curr_Benchmark = None
    is_Ani_running: bool = False
    is_Ani_Paused: bool = False
    tooltip_active: bool = False
    LabelText: None
    warn_again: str = "yes"

    def __init__(Manager, window):
        """
        Initializes the frontend canvas UI.\n
        This also Initializes Game_Manager, FileManager, Canvas_Create and Settings.\n
        The following is being set and done :\n
        Reads each game's patch Info. Creates an array of each available game through the Game_Manager.\n
        Load's the current game's Information.\n
        Handles the entire UI framework, all the canvas, images and ETC.
        """

        Game_Manager.LoadPatches()
        FileManager.Initialize(window, Manager)
        TextureMgr.Initialize()  # load all images.
        Manager.patches = Game_Manager.GetPatches()

        # Save the config string in class variable config
        Manager.config = localconfig

        # Game from config should be chosen here.
        Manager._patchInfo = Manager.patches[2]
        Manager._patchInfo = Game_Manager.GetJsonByID(
            load_config_game(Manager, Manager.config)
        )

        # Load Patch Info for current game.
        Manager.ultracam_beyond = Manager._patchInfo.LoadJson()

        Manager._window = window
        Manager.constyle = Style(theme=theme.lower())
        Manager.constyle.configure("TButton", font=btnfont)

        # ULTRACAM 2.0 PATCHES ARE SAVED HERE.
        Manager.UserChoices = {}
        Manager.setting = Setting(Manager)

        # Read the Current Emulator Mode.
        Manager.mode = config.get("Mode", "managermode", fallback="Legacy")

        # Force to Ryujinx default
        if platform.system() == "Darwin":
            Manager.mode = "Ryujinx"

        # Initialize Json Files.
        Manager.description = load_json("Description.json", descurl)
        Manager.presets = load_json("beyond_presets.json", presetsurl)
        Manager.version_options = load_json("Version.json", versionurl)
        Manager.cheat_options = load_json("Cheats.json", cheatsurl)
        Manager.Legacy_settings = load_json("Legacy_presets.json", Legacy_presets_url)

        # Local text variable
        Manager.switch_text = ttk.StringVar(value="Switch to Ryujinx")
        Manager.cheat_version = ttk.StringVar(value="Version - 1.2.1")

        # Load Canvas
        Load_ImagePath(Manager)
        Manager.load_canvas()
        Manager.switchmode("false")

        # Window protocols
        Manager._window.protocol(
            "WM_DELETE_WINDOW", lambda: Canvas_Create.on_closing(Manager._window)
        )

    def warning(Manager, e):
        messagebox.showwarning(f"{e}")

    def LoadNewGameInfo(Manager):
        """Loads new Game info from the combobox (dropdown Menu)."""
        for item in Manager.patches:
            if Manager.PatchName.get() == item.Name:
                Manager._patchInfo = item
                Manager.ultracam_beyond = Manager._patchInfo.LoadJson()
                pos_dict = copy.deepcopy(Manager.Back_Pos)
                Manager.DeletePatches()
                Manager.LoadPatches(Manager.all_canvas[0], pos_dict)
                Manager.toggle_pages("main")
                save_config_game(Manager, Manager.config)  # comes from config.py
                load_user_choices(Manager, Manager.config)

    def ChangeName(Manager):
        Manager.all_canvas[0].itemconfig(
            Manager.LabelText[0], text=Manager._patchInfo.Name
        )
        Manager.all_canvas[0].itemconfig(
            Manager.LabelText[1], text=Manager._patchInfo.Name
        )

    def LoadPatches(Manager, canvas, pos_dict):
        keys = Manager.ultracam_beyond.get("Keys", [""])

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
                Manager.UserChoices[name] = ttk.StringVar(
                    master=Manager._window, value="auto"
                )
                continue

            if dicts["Class"].lower() == "dropdown":
                patch_var = Canvas_Create.create_combobox(
                    master=Manager._window,
                    canvas=canvas,
                    text=patch_name,
                    values=patch_list,
                    variable=patch_list[patch_default_index],
                    row=pos[0],
                    cul=pos[1],
                    drop_cul=pos[2],
                    width=100,
                    tags=["dropdown", "patchinfo"],
                    tag=section_auto,
                    text_description=patch_description,
                )
                new_pos = increase_row(pos[0], pos[1], pos[2])
                pos[0] = new_pos[0]
                pos[1] = new_pos[1]
                pos[2] = new_pos[2]

            if dicts["Class"].lower() == "scale":
                patch_type = dicts.get("Type")
                patch_increments = dicts.get("Increments")
                patch_var = Canvas_Create.create_scale(
                    master=Manager._window,
                    canvas=canvas,
                    text=patch_name,
                    scale_from=patch_values[0],
                    scale_to=patch_values[1],
                    type=patch_type,
                    row=pos[0],
                    cul=pos[1],
                    drop_cul=pos[2],
                    width=100,
                    increments=float(patch_increments),
                    tags=["scale", "patchinfo"],
                    tag=section_auto,
                    text_description=patch_description,
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
                patch_var = Canvas_Create.create_checkbutton(
                    master=Manager._window,
                    canvas=canvas,
                    text=patch_name,
                    variable="Off",
                    row=pos[3],
                    cul=pos[4],
                    drop_cul=pos[5],
                    tags=["bool", "patchinfo"],
                    tag=section_auto,
                    text_description=patch_description,
                )
                if patch_default_index:
                    patch_var.set("On")
                new_pos = increase_row(pos[3], pos[4], pos[5])
                pos[3] = new_pos[0]
                pos[4] = new_pos[1]
                pos[5] = new_pos[2]

            if patch_var is None:
                continue
            Manager.UserChoices[name] = patch_var

            # Change Name and Load Image.
            Manager.ChangeName()
            Canvas_Create.Change_Background_Image(
                Manager.all_canvas[0],
                os.path.join(Manager._patchInfo.Folder, "image.jpg"),
            )

    def DeletePatches(Manager):
        Manager.UserChoices.clear()
        Manager.all_canvas[0].delete("patchinfo")

    def create_canvas(Manager):

        # clear list.
        Manager.UserChoices = {}

        # Create Canvas
        Manager.maincanvas = ttk.Canvas(
            Manager._window, width=scale(1200), height=scale(600)
        )
        canvas = Manager.maincanvas
        Manager.maincanvas.pack()
        Manager.all_canvas.append(Manager.maincanvas)

        Manager.selected_options = {}

        # Load UI Elements
        load_UI_elements(Manager, Manager.maincanvas)
        create_tab_buttons(Manager, Manager.maincanvas)

        # Create Text Position
        row = 40
        cul_tex = 60
        cul_sel = 220

        # Used for 2nd column.
        row_2 = 160
        cul_tex_2 = 400
        cul_sel_2 = 550

        # Run Scripts for checking OS and finding location
        FileManager.checkpath(Manager.mode)
        FileManager.DetectOS(Manager.mode)

        # FOR DEBUGGING PURPOSES
        def onCanvasClick(event):
            print(f"CRODS = X={event.x} + Y={event.y} + {event.widget}")

        Manager.maincanvas.bind("<Button-3>", onCanvasClick)
        # Start of CANVAS options.

        # Create preset menu.
        presets = {"Saved": {}} | load_json("beyond_presets.json", presetsurl)
        values = list(presets.keys())
        Manager.selected_preset = Canvas_Create.create_combobox(
            master=Manager._window,
            canvas=canvas,
            text="OPTIMIZER PRESETS:",
            variable=values[0],
            values=values,
            row=row,
            cul=cul_tex - 20,
            tags=["text"],
            tag="Optimizer",
            description_name="Presets",
            command=lambda event: apply_selected_preset(Manager),
        )

        # Setting Preset - returns variable.

        # value = ["No Change"]
        # for item in Manager.Legacy_settings:
        #     value.append(item)

        # Manager.selected_settings = Canvas_Create.create_combobox(
        #                                                     master=Manager._window, canvas=canvas,
        #                                                     text="Legacy SETTINGS:",
        #                                                     variable=value[0], values=value,
        #                                                     row=row, cul=340, drop_cul=480,
        #                                                     tags=["text"], tag="Legacy",
        #                                                     description_name="Settings"
        #                                                 )

        value = []
        for item in Manager.patches:
            value.append(item.Name)

        Manager.PatchName = Canvas_Create.create_combobox(
            master=Manager._window,
            canvas=canvas,
            text="Select Game:",
            variable=Manager._patchInfo.Name,
            values=value,
            row=row,
            cul=340,
            drop_cul=430,
            tags=["text"],
            tag="GameSelect",
            description_name="GameSelect",
            command=lambda event: Manager.LoadNewGameInfo(),
        )

        row += 40
        # Create a label for Legacy.exe selection
        backupbutton = cul_sel
        command = lambda event: Manager.select_Legacy_exe()

        def browse():
            Manager.select_Legacy_exe()

        text = "SELECT EXECUTABLE"
        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Browse",
            row=row,
            cul=cul_sel,
            width=6,
            tags=["Button"],
            description_name="Browse",
            command=lambda: browse(),
        )

        # Reset to Appdata
        def Legacy_appdata():
            FileManager.checkpath(Manager.mode)
            superlog.info("Successfully Defaulted to Appdata!")
            save_user_choices(Manager, Manager.config, "appdata", None)

        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Use Appdata",
            row=row,
            cul=cul_sel + 68,
            width=9,
            tags=["Button"],
            description_name="Reset",
            command=Legacy_appdata,
        )

        backupbutton = cul_sel + 165

        Canvas_Create.create_label(
            master=Manager._window,
            canvas=canvas,
            text=text,
            description_name="Browse",
            row=row,
            cul=cul_tex - 20,
            tags=["text"],
            tag=["Select-EXE"],
            outline_tag="outline",
            command=command,
        )

        # Create a Backup button
        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Backup",
            row=row,
            cul=backupbutton,
            width=7,
            tags=["Button"],
            description_name="Backup",
            command=lambda: FileManager.backup(),
        )

        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Clear Shaders",
            row=row,
            cul=backupbutton + 78,
            width=9,
            tags=["Button", "Legacy"],
            description_name="Shaders",
            command=lambda: FileManager.clean_shaders(),
        )

        row += 40

        # Graphics & Extra & More - the -20 is extra
        page_1 = Canvas_Create.image_Button(
            canvas=canvas,
            row=row - 35,
            cul=cul_tex - 10 - 20,
            name="main",
            img_1=TextureMgr.Request("graphics.png"),
            img_2=TextureMgr.Request("graphics_active.png"),
            command=lambda e: Manager.toggle_pages("main"),
            Type=ButtonToggle.StaticDynamic,
        )

        page_2 = Canvas_Create.image_Button(
            canvas=canvas,
            row=row - 35,
            cul=cul_tex + 190 - 10,
            name="extra",
            img_1=TextureMgr.Request("extra.png"),
            img_2=TextureMgr.Request("extra_active.png"),
            command=lambda e: Manager.toggle_pages("extra"),
            Type=ButtonToggle.StaticDynamic,
        )

        Manager.PageBtns.append(page_1)
        Manager.PageBtns.append(page_2)

        # BIG TEXT.
        Manager.LabelText = Canvas_Create.create_label(
            master=Manager._window,
            canvas=canvas,
            text="Tears Of The Kingdom",
            font=bigfont,
            color=BigTextcolor,
            description_name="Mod Improvements",
            anchor="c",
            row=row,
            cul=575,
            tags=["Big-Text", "Middle-Text"],
        )

        row += 40

        ##              AUTO PATCH INFO STARTS HERE ALL CONTROLLED IN JSON FILE.
        ##              THIS IS FOR ULTRACAM BEYOND GRAPHICS AND PERFORMANCE (2.0)
        ##              REMOVED DFPS, SINCE ULTRACAM BEYOND DOES IT ALL AND SO MUCH BETTER.

        pos_dict = {
            "main": [row, cul_tex, cul_sel, row_2, cul_tex_2, cul_sel_2],
            "extra": [row, cul_tex, cul_sel, row_2, cul_tex_2, cul_sel_2],
        }

        Manager.Back_Pos = copy.deepcopy(pos_dict)

        Manager.LoadPatches(canvas, pos_dict)

        row = pos_dict["main"][0]
        row_2 = pos_dict["main"][3]

        Canvas_Create.image_Button(
            canvas=canvas,
            row=510,
            cul=25,
            img_1=TextureMgr.Request("apply.png"),
            img_2=TextureMgr.Request("apply_active.png"),
            command=lambda event: FileManager.submit(),
        )

        # reverse scale.
        Canvas_Create.image_Button(
            canvas=canvas,
            row=510,
            cul=25 + int(TextureMgr.Request("apply.png").width() / sf),
            img_1=TextureMgr.Request("launch.png"),
            img_2=TextureMgr.Request("launch_active.png"),
            command=lambda event: LaunchManager.launch_GAME(Manager, FileManager),
        )

        # extract
        Canvas_Create.image_Button(
            canvas=canvas,
            row=510,
            cul=25 + int(7 + int(TextureMgr.Request("launch.png").width() / sf) * 2),
            img_1=TextureMgr.Request("extract.png"),
            img_2=TextureMgr.Request("extract_active.png"),
            command=lambda event: Manager.extract_patches(),
        )

        Canvas_Create.image_Button(
            canvas=canvas,
            row=520,
            cul=850,
            img_1=TextureMgr.Request("optimizer_logo.png"),
            img_2=TextureMgr.Request("optimizer_logo_active.png"),
            command=lambda event: Manager.open_browser("Kofi"),
        )

        # Load Saved User Options.
        Manager.toggle_pages("main")
        load_user_choices(Manager, Manager.config)
        return Manager.maincanvas

    def update_scaling_variable(Manager, something=None):
        Manager.fps_var.set(Manager.fps_var_new.get())

    def create_cheat_canvas(Manager):
        # Create Cheat Canvas
        Manager.cheatcanvas = ttk.Canvas(
            Manager._window, width=scale(1200), height=scale(600)
        )

        Manager.cheatcanvas.pack(expand=1, fill=BOTH)
        canvas = Manager.cheatcanvas
        Manager.all_canvas.append(Manager.cheatcanvas)

        # Create UI elements.
        Manager.Cheat_UI_elements(Manager.cheatcanvas)
        create_tab_buttons(Manager, Manager.cheatcanvas)

        # Push every version in combobox
        versionvalues = []
        for each in Manager.cheat_options:
            for key, value in each.items():
                if key == "Aversion":
                    versionvalues.append("Version - " + value)

        Manager.cheat_version = Canvas_Create.create_combobox(
            master=Manager._window,
            canvas=canvas,
            text="",
            values=versionvalues,
            variable=versionvalues[1],
            row=520,
            cul=130 + 2,
            drop_cul=130 + 2,
            tags=["text"],
            tag=None,
            description_name="CheatVersion",
            command=lambda event: loadCheats(),
        )

        load_user_choices(Manager, Manager.config)

        def loadCheats():
            row = 40
            cul_tex = 40
            cul_sel = 200

            corrent_cheats = Manager.cheat_options[
                versionvalues.index(Manager.cheat_version.get())
            ].items()
            corrent_cheats_dict = dict(corrent_cheats)
            sorted_cheats = dict(
                sorted(corrent_cheats_dict.items(), key=lambda item: item[0])
            )
            try:
                for key_var, value in Manager.selected_cheats.items():
                    value = value.get()
                    Manager.old_cheats[key_var] = value
            except AttributeError as e:
                Manager.old_cheats = {}

            Manager.selected_cheats = {}

            Manager.cheatcanvas.delete("cheats")

            for version_option_name, version_option_value in sorted_cheats.items():
                # Exclude specific keys from being displayed
                if version_option_name in ["Source", "nsobid", "offset", "version"]:
                    continue

                # Create label
                if version_option_name not in [
                    "Source",
                    "Version",
                    "Aversion",
                    "Cheat Example",
                ]:

                    version_option_var = Canvas_Create.create_checkbutton(
                        master=Manager._window,
                        canvas=canvas,
                        text=version_option_name,
                        variable="Off",
                        row=row,
                        cul=cul_tex,
                        drop_cul=cul_sel,
                        tags=["text"],
                        tag="cheats",
                        description_name=version_option_name,
                    )

                    # Create enable/disable dropdown menu
                    try:
                        if Manager.old_cheats.get(version_option_name) == "On":
                            version_option_var.set("On")
                    except AttributeError as e:
                        Manager.old_cheats = {}
                    Manager.selected_cheats[version_option_name] = version_option_var
                else:
                    continue

                row += 40

                if row > 480:
                    row = 40
                    cul_tex += 200
                    cul_sel += 200

        def ResetCheats():
            try:
                for key, value in Manager.selected_cheats.items():
                    value.set("Off")
            except AttributeError as e:
                log.error(
                    f"Error found from ResetCheats, the script will continue. {e}"
                )

        # Create a submit button
        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Apply Cheats",
            row=520,
            cul=39,
            width=9,
            padding=5,
            tags=["Button"],
            style="success",
            description_name="Apply Cheats",
            command=lambda: FileManager.submit(),
        )

        # Create a submit button
        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Reset Cheats",
            row=520,
            cul=277 + 6 + 2,
            width=8,
            padding=5,
            tags=["Button"],
            style="default",
            description_name="Reset Cheats",
            command=ResetCheats,
        )

        # Read Cheats
        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Read Saved Cheats",
            row=520,
            cul=366 + 2,
            width=11,
            padding=5,
            tags=["Button"],
            style="default",
            description_name="Read Cheats",
            command=lambda: load_user_choices(Manager, Manager.config, "Cheats"),
        )

        # Backup
        Canvas_Create.create_button(
            master=Manager._window,
            canvas=canvas,
            text="Backup",
            row=520,
            cul=479 + 2,
            width=7,
            padding=5,
            tags=["Button"],
            style="default",
            description_name="Backup",
            command=lambda: FileManager.backup(),
        )

        loadCheats()
        load_user_choices(Manager, Manager.config)

    def select_Legacy_exe(Manager):
        if Manager.os_platform == "Windows":
            Legacy_path = filedialog.askopenfilename(
                title=f"Please select {Manager.mode}.exe",
                filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")],
            )

            executable_name = Legacy_path
            if executable_name.endswith("Ryujinx.exe") or executable_name.endswith(
                "Ryujinx.Ava.exe"
            ):
                if Manager.mode == "Legacy":
                    Manager.switchmode("true")
            else:
                if Manager.mode == "Ryujinx":
                    Manager.switchmode("true")

            if Legacy_path:
                # Save the selected Legacy.exe path to a configuration file
                save_user_choices(Manager, Manager.config, Legacy_path)
                home_directory = os.path.dirname(Legacy_path)
                fullpath = os.path.dirname(Legacy_path)
                if any(item in os.listdir(fullpath) for item in ["user", "portable"]):
                    superlog.info(
                        f"Successfully selected {Manager.mode}.exe! And a portable folder was found at {home_directory}!"
                    )
                    FileManager.checkpath(Manager.mode)
                    return Legacy_path
                else:
                    superlog.info(
                        f"Portable folder for {Manager.mode} not found defaulting to appdata directory!"
                    )
                    FileManager.checkpath(Manager.mode)
                    return Legacy_path
            else:
                FileManager.checkpath(Manager.mode)
                return None

        if Manager.os_platform == "Linux":
            Legacy_path = filedialog.askopenfilename(
                title=f"Please select {Manager.mode}.AppImage",
                filetypes=[
                    ("Select AppImages or Executable: ", "*.*"),
                    ("All Files", "*.*"),
                ],
            )

            executable_name = Legacy_path

            if executable_name.startswith("Ryujinx") or executable_name.startswith(
                "Ryujinx.ava"
            ):
                if Manager.mode == "Legacy":
                    Manager.switchmode("true")
            else:
                if Manager.mode == "Ryujinx":
                    Manager.switchmode("true")

            save_user_choices(Manager, Manager.config, Legacy_path)
        return Legacy_path

    def show_main_canvas(Manager):
        Canvas_Create.is_Ani_Paused = True
        Manager.cheatcanvas.pack_forget()
        Manager.maincanvas.pack()

    def toggle_pages(Manager, ShowPage: str):
        Manager.maincanvas.itemconfig(ShowPage, state="normal")

        for button in Manager.PageBtns:
            if button.Name != ShowPage:
                Manager.maincanvas.itemconfig(button.Name, state="hidden")
                log.info(f"Hiding {button.Name}")
                button.set(False)
                button.ToggleImg(WidgetState.Leave)
            else:
                button.ToggleImg(WidgetState.Enter)

    def show_cheat_canvas(Manager):
        Canvas_Create.is_Ani_Paused = False
        Manager.cheatcanvas.pack()
        Manager.maincanvas.pack_forget()

        Manager.ani = threading.Thread(
            name="cheatbackground",
            target=lambda: Canvas_Create.canvas_animation(
                Manager._window, Manager.cheatcanvas
            ),
        )

        if not Manager.is_Ani_running == True:
            Manager.is_Ani_running = True
            Manager.ani.start()

    def open_browser(Manager, web, event=None):
        url = "https://ko-fi.com/maxlastbreath#"
        if web == "Kofi":
            url = "https://ko-fi.com/maxlastbreath#"
        elif web == "Github":
            url = "https://github.com/MaxLastBreath/TOTK-mods"
        elif web == "Discord":
            url = "https://discord.gg/7MMv4yGfhM"
        webbrowser.open(url)

    def load_canvas(Manager):
        # Main
        Manager.create_canvas()
        Manager.create_cheat_canvas()
        Manager.cheatcanvas.pack_forget()
        load_benchmark(Manager)

    def Cheat_UI_elements(Manager, canvas):
        Manager.cheatbg = canvas.create_image(
            0,
            -scale(300),
            anchor="nw",
            image=TextureMgr.Request("image_cheats.png"),
            tags="background",
        )
        canvas.create_image(
            0,
            0,
            anchor="nw",
            image=TextureMgr.Request("Legacy_BG.png"),
            tags="overlay-1",
        )
        canvas.create_image(
            0,
            0,
            anchor="nw",
            image=TextureMgr.Request("BG_Left_Cheats.png"),
            tags="overlay",
        )

    def switchmode(Manager, command="true"):
        if command == "true":
            if Manager.mode == "Legacy":
                Manager.mode = "Ryujinx"
                for canvas in Manager.all_canvas:
                    # canvas.itemconfig("overlay-1", image=TextureMgr.Request("Ryujinx_BG.png"))
                    # canvas.itemconfig("information", text=f"{Manager.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="hidden")

                if Manager.os_platform == "Darwin":
                    Manager.switch_text.set("Only Ryujinx supported")
                else:
                    Manager.switch_text.set("Switch to Legacy")
                return

            elif Manager.mode == "Ryujinx" and Manager.os_platform != "Darwin":
                Manager.mode = "Legacy"
                for canvas in Manager.all_canvas:
                    # canvas.itemconfig("overlay-1", image=TextureMgr.Request("Legacy_BG.png"))
                    # canvas.itemconfig("information", text=f"{Manager.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="normal")
                # change text
                Manager.switch_text.set("Switch to Ryujinx")
                return

        elif command == "false":
            if Manager.mode == "Ryujinx":
                for canvas in Manager.all_canvas:
                    # canvas.itemconfig("overlay-1", image=TextureMgr.Request("Ryujinx_BG.png"))
                    # canvas.itemconfig("information", text=f"{Manager.mode} TOTK Optimizer")
                    canvas.itemconfig("Legacy", state="hidden")
                if Manager.os_platform == "Darwin":
                    Manager.switch_text.set("Only Ryujinx supported")
                else:
                    Manager.switch_text.set("Switch to Legacy")
                return

        elif command == "Mode":
            return Manager.mode

    def fetch_var(Manager, var, dict, option):
        if not dict.get(option, "") == "":
            var.set(dict.get(option, ""))

    def extract_patches(Manager):
        FileManager.is_extracting = True
        FileManager.submit()
