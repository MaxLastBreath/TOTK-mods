from configuration.settings import *
from configuration.settings_config import Setting
from modules.TOTK_Optimizer_Modules import *  # imports all needed files.
from modules.GameManager.GameManager import Game_Manager
from modules.GameManager.PatchInfo import PatchInfo
from modules.GameManager.FileManager import FileManager
from modules.GameManager.LaunchManager import LaunchManager
from modules.GameManager.CheatManager import Cheats
from modules.FrontEnd.TextureMgr import TextureMgr
from modules.FrontEnd.Localization import Localization
from modules.load_elements import create_tab_buttons, load_UI_elements
from modules.FrontEnd.FrontEndMode import NxMode
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

    _patchInfo: PatchInfo = None
    _window: ttk.Window
    _Cheats: Cheats = None

    patches: list[PatchInfo] = []
    all_canvas: list[ttk.Canvas] = []
    PageBtns: list[ImageButton] = []

    _EmulatorScale: ttk.Variable = None
    old_cheats: dict = {}
    benchmarks: dict = {}

    constyle: ttk.Style
    os_platform: str = platform.system()

    Curr_Benchmark = None
    is_Ani_running: bool = False
    is_Ani_Paused: bool = False
    tooltip_active: bool = False
    LabelText: None
    warn_again: str = "yes"

    ModeType: ImageButton

    def __init__(Manager, window):

        """
        Initializes the frontend canvas UI.\n
        This also Initializes Game_Manager, FileManager, Canvas_Create and Settings.\n
        The following is being set and done :\n
        Reads each game's patch Info. Creates an array of each available game through the Game_Manager.\n
        Load's the current game's Information.\n
        Handles the entire UI framework, all the canvas, images and ETC.
        """

        from modules.FrontEnd.AnimationMgr import AnimationQueue

        Manager._window = window

        Game_Manager.LoadPatches()
        FileManager.Initialize(window, Manager)
        TextureMgr.Initialize()  # load all images.
        AnimationQueue.Initialize()
        Manager.patches = Game_Manager.GetPatches()
        
        # Emulator Scaling
        Manager._EmulatorScale = ttk.Variable(master=window, value=1)

        # Save the config string in class variable config
        Manager.config = localconfig

        # Game from config should be chosen here.
        Manager._patchInfo = Manager.patches[-1]
        Manager._patchInfo = Game_Manager.GetJsonByID(
            load_config_game(Manager, Manager.config)
        )

        Cheats.Initialize(Manager, Manager._patchInfo)
        Manager._Cheats = Cheats  # Store class because circular bs

        # Load Patch Info for current game.
        Manager.ultracam_beyond = Manager._patchInfo.LoadJson()

        # Load Localization
        Manager.description = Localization.GetJson()
        Manager.constyle = Style(theme=theme.lower())
        Manager.constyle.configure("TButton", font=btnfont)

        # ULTRACAM 2.0 PATCHES ARE SAVED HERE.
        Manager.UserChoices = {}
        Manager.setting = Setting(Manager)

        # Local text variable
        Manager.cheat_version = ttk.StringVar(value="Version - 1.2.1")

        # Load Canvas
        # Load_ImagePath(Manager)
        Manager.Create_Canvases()

        # Load NX-Mode, CheckPaths and Print User OS.
        NxMode.Initialize(Manager.all_canvas, FileManager)
        FileManager.checkpath()
        FileManager.DetectOS()

        # Load Benchmark at the very end
        Benchmark.Initialize(Manager, FileManager)
        Manager.ForceGameBG()

        # Window protocols
        Manager._window.protocol(
            "WM_DELETE_WINDOW", lambda: Canvas_Create.on_closing(Manager._window)
        )

    def warning(Manager, e):
        messagebox.showwarning(f"{e}")

    def ForceGameBG(Manager):
        # Change Name and Load Image.
        Manager.ChangeName()

        for canvas in Manager.all_canvas:
            Canvas_Create.Change_Background_Image(
                canvas,
                os.path.join(Manager._patchInfo.Folder, "image.jpg"),
            )

    def LoadNewGameInfo(Manager):
        """Loads new Game info from the combobox (dropdown Menu)."""
        for item in Manager.patches:
            if Manager.PatchName.get() == item.Name:
                Manager._patchInfo = item
                Cheats.Initialize(Manager, item)
                Manager.ultracam_beyond = Manager._patchInfo.LoadJson()
                pos_dict = copy.deepcopy(Manager.Back_Pos)

                # DeletePatches and Load New Patches.
                Manager.DeletePatches()
                Manager.LoadPatches(Manager.all_canvas[0], pos_dict)
                Manager.toggle_pages("main")
                Manager.ForceGameBG()
                Manager.CreatePresets()

                # Save the selected game in the config file and load options for that game.
                save_config_game(Manager, Manager.config)
                load_user_choices(Manager, Manager.config)

                Cheats.loadCheats()  # load the new cheats.
                Cheats.LoadCheatsConfig()
                FileManager.checkpath()
                Benchmark.ReloadBenchmarkInfo()

    def ChangeName(Manager):
        Manager.all_canvas[0].itemconfig(
            Manager.LabelText[0], text=Manager._patchInfo.Name
        )
        Manager.all_canvas[0].itemconfig(
            Manager.LabelText[1], text=Manager._patchInfo.Name
        )

    def UpdateEmuScale(Manager, canvas: ttk.Canvas, variable: ttk.Variable, name: str):
        keys = Manager.ultracam_beyond.get("Keys", [""])
        try:
            if (Manager.UserChoices["resolution"] is not None):
                Resolution = Manager.UserChoices["resolution"].get()
                Resolution = re.findall(r"\d+", Resolution)
                canvas.itemconfig(name, text=str(int(int(Resolution[0]) * float(variable.get()))) + "p")
        except Exception:
            canvas.itemconfig(name, text=str(int(900 * float(variable.get()))) + "p")

    def LoadPatches(Manager, canvas, pos_dict):
        ResolutionScaleName = "Resolution Scale"

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
                    command=(lambda e: Manager.UpdateEmuScale(canvas, Manager._EmulatorScale, ResolutionScaleName)) if name == "resolution" else None
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

        section_auto = dicts.get("Section")
        pos = pos_dict[section_auto]

        if (Manager._patchInfo.ResolutionScale is True):
            Manager._EmulatorScale = Canvas_Create.create_scale(
                master=Manager._window,
                canvas=canvas,
                text=ResolutionScaleName,
                scale_from=int(1),
                scale_to=int(4),
                type="s32",
                row=pos[0],
                cul=pos[1],
                drop_cul=pos[2],
                width=100,
                increments=int(1),
                tags=["scale", "patchinfo"],
                tag="Main",
                text_description="ResScale",
                command=lambda e: Manager.UpdateEmuScale(canvas, Manager._EmulatorScale, ResolutionScaleName)
            )
            Manager._EmulatorScale.set(1)
        
    def DeletePatches(Manager):
        Manager.UserChoices.clear()
        Manager.all_canvas[0].delete("patchinfo")

    def CreatePresets(Manager, row=40, cul_tex=60, cul_sel=220):

        Manager.maincanvas.delete("OptimizerPresets")

        # Create preset menu.
        presets = Manager._patchInfo.LoadPresetsJson()
        values = list(presets.keys())
        Manager.selected_preset = Canvas_Create.create_combobox(
            master=Manager._window,
            canvas=Manager.maincanvas,
            text="OPTIMIZER PRESETS:",
            variable=values[0],
            values=values,
            row=row,
            cul=cul_tex - 20,
            tags=["text"],
            tag="OptimizerPresets",
            description_name="Presets",
            command=lambda event: apply_selected_preset(Manager),
        )

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

        Manager.CreatePresets()

        # FOR DEBUGGING PURPOSES
        def onCanvasClick(event):
            print(f"CRODS = X={event.x} + Y={event.y} + {event.widget}")

        Manager.maincanvas.bind("<Button-3>", onCanvasClick)
        # Start of CANVAS options.

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
            command=lambda e: Manager.LoadNewGameInfo(),
        )

        row += 40
        # Create a label for Legacy.exe selection
        backupbutton = cul_sel
        command = lambda e: Manager.select_Legacy_exe()

        def browse():
            Manager.select_Legacy_exe()

        text = "SELECT EXECUTABLE"
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

        Offset = 170

        btn = Canvas_Create.image_Button(
            canvas=canvas,
            row=row - 5,
            cul=cul_tex + Offset,
            name="browse",
            anchor="c",
            img_1=TextureMgr.Request("browse.png"),
            img_2=TextureMgr.Request("browse_a.png"),
            command=lambda e: browse(),
            tags=["Button"],
        )

        # Reset to Appdata
        def appdata():
            save_user_choices(Manager, Manager.config, "appdata")
            superlog.info("Successfully Defaulted to Appdata!")
            FileManager.checkpath()

        btn = Canvas_Create.image_Button(
            canvas=canvas,
            row=row - 5,
            cul=cul_tex + Offset + 92,
            name="appdata",
            anchor="c",
            img_1=TextureMgr.Request("autosearch.png"),
            img_2=TextureMgr.Request("autosearch_a.png"),
            command=lambda e: appdata(),
            tags=["Button"],
        )

        backupbutton = cul_sel + 165

        # Create a Backup button
        btn = Canvas_Create.image_Button(
            canvas=canvas,
            row=row - 5,
            cul=cul_tex + Offset + 92 * 2,
            name="backup",
            anchor="c",
            img_1=TextureMgr.Request("backup.png"),
            img_2=TextureMgr.Request("backup_a.png"),
            command=lambda e: FileManager.backup(),
            tags=["Button"],
        )

        btn = Canvas_Create.image_Button(
            canvas=canvas,
            row=row - 5,
            cul=cul_tex + Offset + 92 * 3,
            name="shaders",
            anchor="c",
            img_1=TextureMgr.Request("shaders.png"),
            img_2=TextureMgr.Request("shaders_a.png"),
            command=lambda e: FileManager.clean_shaders(),
            tags=["Button"],
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
            isOn=True,
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

        Manager.ModeType = Canvas_Create.image_Button(
            canvas=canvas,
            row=50,
            cul=620 + 60,
            anchor="c",
            img_1=TextureMgr.Request("Switch_Button.png"),
            img_2=TextureMgr.Request("Switch_Button_active.png"),
            command=lambda event: NxMode.switch(),
            Type=ButtonToggle.Static,
            tags=["Ryujinx"]
        )

        Manager.ModeType = Canvas_Create.image_Button(
            canvas=canvas,
            row=50,
            cul=620 + 60,
            anchor="c",
            img_1=TextureMgr.Request("Switch_Button_2.png"),
            img_2=TextureMgr.Request("Switch_Button_2_active.png"),
            command=lambda event: NxMode.switch(),
            Type=ButtonToggle.StaticDynamic,
            tags=["Legacy"]
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

        Logo = Canvas_Create.image_Button(
            canvas=canvas,
            row=560,
            cul=1010,
            anchor="c",
            img_1=TextureMgr.Request("optimizer_logo.png"),
            img_2=TextureMgr.Request("optimizer_logo_active.png"),
            command=lambda event: Manager.open_browser("Web"),
        )

        Logo._Images.pop()

        for i in range(1, 6):
            Logo._Images.append(
                TextureMgr.Request(f"LogoAnimation/Logo_Active_{i}.png")
            )

        # Load Saved User Options.
        Manager.toggle_pages("main")
        load_user_choices(Manager, Manager.config)
        return Manager.maincanvas

    def select_Legacy_exe(Manager):
        if Manager.os_platform == "Windows":
            Legacy_path = filedialog.askopenfilename(
                title=f"Please select the Emulator Executable File (.exe)",
                filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")],
            )

            executable_name = Legacy_path
            if executable_name.endswith("Ryujinx.exe") or executable_name.endswith("Ava.exe"):
                NxMode.set("Ryujinx")
            else:
                NxMode.set("Legacy")

            if Legacy_path:
                # Save the selected Legacy.exe path to a configuration file
                save_user_choices(Manager, Manager.config, Legacy_path)
                home_directory = os.path.dirname(Legacy_path)
                fullpath = os.path.dirname(Legacy_path)
                if any(item in os.listdir(fullpath) for item in ["user", "portable"]):
                    superlog.info(
                        f"Successfully selected {NxMode.get()}.exe! And a portable folder was found at {home_directory}!"
                    )
                    FileManager.checkpath()
                    return Legacy_path
                else:
                    superlog.info(
                        f"Portable folder for {NxMode.get()} not found defaulting to appdata directory!"
                    )
                    FileManager.checkpath()
                    return Legacy_path
            else:
                return None

        if Manager.os_platform == "Linux":
            Legacy_path = filedialog.askopenfilename(
                title=f"Please select {NxMode.get()}.AppImage",
                filetypes=[
                    ("Select AppImages or Executable: ", "*.*"),
                    ("All Files", "*.*"),
                ],
            )

            executable_name = Legacy_path

            if executable_name.startswith("Ryujinx") or executable_name.startswith(
                "Ryujinx.ava"
            ):
                NxMode.set("Ryujinx")

            save_user_choices(Manager, Manager.config, Legacy_path)
        return Legacy_path

    def Create_Canvases(Manager):
        # Main
        Manager.create_canvas()
        Cheats.CreateCanvas(Manager)
        Cheats.Hide()

    def show_main_canvas(Manager):
        Canvas_Create.is_Ani_Paused = True
        Cheats.Hide()
        Manager.maincanvas.pack()

    def show_cheat_canvas(Manager):
        Canvas_Create.is_Ani_Paused = False
        if Manager._patchInfo.Cheats is False:
            return

        for canvas in Manager.all_canvas:
            if canvas is not Cheats.Canvas:
                canvas.pack_forget()

        Cheats.Show()

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

    def open_browser(Manager, web, event=None):
        url = "https://www.nxoptimizer.com/"
        if web == "Kofi":
            url = "https://www.nxoptimizer.com/ko-fi/"
        elif web == "Github":
            url = "https://www.nxoptimizer.com/"
        elif web == "Discord":
            url = "https://www.nxoptimizer.com/discord/"
        elif web == "Web":
            url = "https://www.nxoptimizer.com/"
        webbrowser.open(url)

    def extract_patches(Manager):
        FileManager.is_extracting = True
        FileManager.submit()
