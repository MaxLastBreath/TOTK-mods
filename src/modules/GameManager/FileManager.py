from modules.FrontEnd.ProgressBar import ProgressBar
from configuration.settings_config import Setting
from modules.TOTK_Optimizer_Modules import *
from configuration.settings import *
from modules.config import *
from tkinter import ttk
import threading
import re

class FileManager:

    _window = None
    _frontend = None

    is_extracting = False
    mode = "Legacy"

    configdir = str
    TOTKconfig = str
    nand_dir = str
    ryujinx_config = str
    sdmc = str
    load_dir = str
    Legacydir = str
    Globaldir = str

    @classmethod
    # Initialize our Window here.
    def Initialize(cls, Window, FrontEnd):
        cls._frontend = FrontEnd
        cls._window = Window

    @classmethod
    def GetClass(cls):
        return cls

    @classmethod
    def load_Legacy_path(cls, config_file):
        if cls.mode == "Legacy":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            Legacy_path = config.get('Paths', 'Legacypath', fallback="Appdata")
            return Legacy_path
        if cls.mode == "Ryujinx":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            ryujinx_path = config.get('Paths', 'ryujinxpath', fallback="Appdata")
            return ryujinx_path
    
    @classmethod
    def checkpath(cls, mode):
        if cls.is_extracting is True:
            cls.configdir = None
            cls.TOTKconfig = None
            cls.nand_dir = None
            cls.ryujinx_config = None
            cls.sdmc = None
            cls.load_dir = os.getcwd()
            cls.Legacydir = os.getcwd()
            cls.Globaldir = os.getcwd()
            return

        home_directory = os.path.expanduser("~")
        # Default Dir for Linux/SteamOS
        cls.os_platform = platform.system()
        if cls.os_platform == "Linux":
            if mode == "Legacy":
                flatpak = os.path.join(home_directory, ".var", "app", "org.yuzu_emu.yuzu", "config", "yuzu")
                steamdeckdir = os.path.join(home_directory, ".config", "yuzu", "qt-config.ini")

                cls.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")
                cls.configdir = os.path.join(cls.Globaldir, "config", "qt-config.ini")
                cls.TOTKconfig = os.path.join(cls.Globaldir, "config", "custom")

                # Assume it's a steamdeck
                if os.path.exists(steamdeckdir):
                    log.info("Detected a steamdeck!")
                    cls.configdir = steamdeckdir
                    cls.TOTKconfig = os.path.join(home_directory, ".config", "yuzu", "custom")

                # Find any "Legacy Emulators"...
                local_dir = os.path.join(home_directory, ".local", "share")
                for folder in os.listdir(local_dir):
                    cls.Globaldir = os.path.join(local_dir, folder)
                    if os.path.exists(os.path.join(cls.Globaldir, "load", "0100F2C0115B6000")):
                        print(f"Found Legacy Emu folder at: {cls.Globaldir}")
                        cls.configdir = os.path.join(cls.Globaldir, "qt-config.ini")
                        cls.TOTKconfig = os.path.join(cls.Globaldir, "custom")
                        new_path = os.path.dirname(os.path.dirname(cls.Globaldir))
                        cls.Globaldir = os.path.join(new_path, "data", "yuzu")
                        break
                    else:
                        cls.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")

                # Find any "Legacy Emulators" on flatpak...
                flatpak_dir = os.path.join(home_directory, ".var", "app")
                for folder in os.listdir(local_dir):
                    cls.Globaldir = os.path.join(local_dir, folder, "config", "yuzu")
                    if os.path.exists(os.path.join(cls.Globaldir, "load", "0100F2C0115B6000")):
                        print(f"Found Legacy Emu folder at: {cls.Globaldir}")
                        cls.configdir = os.path.join(cls.Globaldir, "qt-config.ini")
                        cls.TOTKconfig = os.path.join(cls.Globaldir, "custom")
                        new_path = os.path.dirname(os.path.dirname(cls.Globaldir))
                        cls.Globaldir = os.path.join(new_path, "data", "yuzu")
                        break
                    else:
                        cls.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")

                config_parser = configparser.ConfigParser()
                config_parser.read(cls.configdir, encoding="utf-8")
                cls.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{cls.Globaldir}/nand')).replace('"', "")
                cls.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{cls.Globaldir}/sdmc')).replace('"', "")
                if cls.nand_dir.startswith('"'):
                    cls.nand_dir = cls.nand_dir.strip('"')[0]
                cls.load_dir = os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{cls.Globaldir}/load')).replace('"', "")
                if cls.nand_dir.startswith('"'):
                    cls.nand_dir = cls.nand_dir.strip('"')[0]
                cls.load_dir = os.path.join(cls.load_dir, "0100F2C0115B6000")

                cls.Legacydir = os.path.normpath(os.path.join(home_directory, ".local", "share", "yuzu", "load", "0100F2C0115B6000"))
                return

            if mode == "Ryujinx":
                cls.Globaldir = os.path.join(home_directory, ".config", "Ryujinx")
                flatpak = os.path.join(home_directory, ".var", "app", "org.ryujinx.Ryujinx", "config", "Ryujinx")

                if os.path.exists(flatpak):
                    log.info("Detected a Ryujinx flatpak!")
                    cls.Globaldir = flatpak
                    cls.nand_dir = os.path.join(f"{cls.Globaldir}", "bis", "user", "save")
                    cls.sdmc_dir = os.path.join(f"{cls.Globaldir}", "sdcard")
                    cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", "0100f2c0115b6000")
                    cls.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents",
                                                "0100f2c0115b6000")
                    cls.ryujinx_config = os.path.join(cls.Globaldir, "Config.json")
                    return

                cls.configdir = None
                cls.TOTKconfig = None
                cls.nand_dir = os.path.join(f"{cls.Globaldir}", "bis", "user", "save")
                cls.sdmc_dir = os.path.join(f"{cls.Globaldir}", "sdcard")
                cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", "0100f2C0115B6000")
                cls.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                cls.ryujinx_config = os.path.join(cls.Globaldir, "Config.json")
                return
        # Default Dir for Windows or user folder.
        elif cls.os_platform == "Windows":
            Legacypath = cls.load_Legacy_path(localconfig)
            userfolder = os.path.normpath(os.path.join(Legacypath, "../user/"))
            portablefolder = os.path.normpath(os.path.join(Legacypath, "../portable/"))
            # Check for user folder
            if mode == "Legacy":
                # Find any "Legacy Emulators"...
                appdata = os.path.join(home_directory, "AppData", "Roaming")
                for folder in os.listdir(appdata):
                    cls.Globaldir = os.path.join(appdata, folder)
                    if os.path.exists(os.path.join(cls.Globaldir, "load", "0100F2C0115B6000")):
                        print(f"Found Legacy Emu folder at: {cls.Globaldir}")
                        break
                    else:
                        cls.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "yuzu")

                if os.path.exists(userfolder):
                    cls.configdir = os.path.join(Legacypath, "../user/config/qt-config.ini")
                    cls.TOTKconfig = os.path.join(cls.configdir, "../custom")
                    config_parser = configparser.ConfigParser()
                    config_parser.read(cls.configdir, encoding="utf-8")
                    cls.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{os.path.join(Legacypath, "../user/nand")}')).replace('"', "")
                    cls.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{os.path.join(Legacypath, "../user/sdmc")}')).replace('"', "")
                    if cls.nand_dir.startswith('"'):
                        cls.nand_dir = cls.nand_dir.strip('"')[0]
                    cls.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{os.path.join(Legacypath, "../user/nand")}')), "0100F2C0115B6000").replace('"', "")
                    if cls.load_dir.startswith('"'):
                        cls.load_dir = cls.load_dir.strip('"')[0]
                    cls.Legacydir = os.path.join(cls.Globaldir, "load", "0100F2C0115B6000").replace('"', "")
                    NEWLegacy_path = os.path.normpath(os.path.join(userfolder, "../"))
                    cls.Globaldir = os.path.join(NEWLegacy_path, "user")
                    qt_config_save_dir = os.path.normpath(os.path.join(cls.nand_dir, "../../"))
                    # Warn user that their QT-Config path is INCORRECT!
                    if qt_config_save_dir != NEWLegacy_path and cls.warn_again == "yes":
                        message = (
                            f"WARNING: Your QT Config Save Directory may not be correct!\n"
                            f"Your saves could be in danger.\n"
                            f"Your current Legacy directory: {NEWLegacy_path}\n"
                            f"Your QT Config Save Directory: {qt_config_save_dir}\n"
                            f"Do you want to create a backup of your save file?"
                        )
                        response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)
                        if response:
                            cls.backup()
                            cls.warn_again = "no"
                            log.info("Sucessfully backed up save files, in backup folder. "
                                    "Please delete qt-config in USER folder! "
                                    "Or correct the user folder paths, then use the backup file to recover your saves!")
                            pass
                        else:
                            cls.warn_again = "no"
                            log.info("Warning has been declined, "
                                    "no saves have been moved!")
                    return
                # Default to Appdata
                else:
                    cls.configdir = os.path.join(cls.Globaldir, "config", "qt-config.ini")
                    cls.TOTKconfig = os.path.join(cls.configdir, "../custom")
                    config_parser = configparser.ConfigParser()
                    config_parser.read(cls.configdir, encoding="utf-8")
                    cls.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{cls.Globaldir}/nand')).replace('"', "").replace('"', "")
                    cls.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{cls.Globaldir}/sdmc')).replace('"', "").replace('"', "")
                    if cls.nand_dir.startswith('"'):
                        cls.nand_dir = cls.nand_dir.strip('"')[0]
                    cls.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{cls.Globaldir}/load')), "0100F2C0115B6000").replace('"', "")
                    if cls.load_dir.startswith('"'):
                        cls.load_dir = cls.load_dir.strip('"')[0]
                    cls.Legacydir = os.path.join(cls.Globaldir, "load", "0100F2C0115B6000")


                    return
            if mode == "Ryujinx":
                if os.path.exists(portablefolder):
                    cls.configdir = None
                    cls.TOTKconfig = None
                    cls.ryujinx_config = os.path.join(portablefolder, "Config.json")
                    cls.nand_dir = os.path.join(f"{portablefolder}", "bis", "user", "save")
                    cls.load_dir = os.path.join(f"{portablefolder}", "mods", "contents", "0100f2C0115b6000")
                    cls.sdmc_dir = os.path.join(f"{portablefolder}", "sdcard")
                    cls.Legacydir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                    return
                else:
                    cls.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx")
                    cls.configdir = None
                    cls.TOTKconfig = None
                    cls.ryujinx_config = os.path.join(cls.Globaldir, "Config.json")
                    cls.nand_dir = os.path.join(f"{cls.Globaldir}", "bis", "user", "save")
                    cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", "0100f2C0115b6000")
                    cls.sdmc_dir = os.path.join(f"{cls.Globaldir}", "sdcard")
                    cls.Legacydir = cls.load_dir
                    return
        elif cls.os_platform == "Darwin":
            if mode == "Ryujinx":
                cls.Globaldir = os.path.join(home_directory, "Library", "Application Support", "Ryujinx")
                cls.configdir = None
                cls.TOTKconfig = None
                cls.ryujinx_config = os.path.join(cls.Globaldir, "Config.json")
                cls.nand_dir = os.path.join(f"{cls.Globaldir}", "bis", "user", "save")
                cls.sdmc_dir = os.path.join(f"{cls.Globaldir}", "sdcard")
                cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", "0100f2C0115B6000")
                cls.Legacydir = cls.load_dir
                return


        # Ensure the path exists.
        try:
            # attempt to create qt-config.ini directories in case they don't exist. Give error to warn user
            os.makedirs(cls.nand_dir, exist_ok=True)
            os.makedirs(cls.load_dir, exist_ok=True)
            os.makedirs(cls.Legacydir, exist_ok=True)
        except PermissionError as e:
            log.warrning(f"Unable to create directories, please run {cls.mode}, {e}")
            cls.warning(f"Unable to create directories, please run {cls.mode}, {e}")

    @classmethod
    def DetectOS(cls, mode):
        if cls.os_platform == "Linux":
            log.info("Detected a Linux based SYSTEM!")
        elif cls.os_platform == "Windows":
            log.info("Detected a Windows based SYSTEM!")
            if mode == "Legacy":
                if os.path.exists(cls.configdir):
                    log.info("a qt-config.ini file found!")
                else:
                    log.warning("qt-config.ini not found, the script will assume default appdata directories, "
                                "please reopen Legacy for consistency and make sure TOTK is present..!")
        elif cls.os_platform == "Darwin":
            log.info("Detected a MacOS based SYSTEM!")

    @classmethod
    def submit(cls, mode=None):
        cls.add_list = []
        cls.remove_list = []
        cls.checkpath(mode)
        # Needs to be run after checkpath.
        if cls.mode == "Legacy":
            qtconfig = get_config_parser()
            qtconfig.optionxform = lambda option: option
            try:
                qtconfig.read(cls.configdir)
            except Exception as e: log.warning(f"Couldn't' find QT-config {e}")
        else:
            qtconfig = None

        def timer(value):
            ProgressBar.progress_bar["value"] = value
            cls._window.update_idletasks()

        def run_tasks():
            if mode == "Cheats":
                log.info("Starting TASKs for Cheat Patch..")
                tasklist = [Create_Mod_Patch("Cheats")]
                if get_setting("cheat-backup") in ["On"]:
                    tasklist.append(backup(cls))
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                ProgressBar.Destroy()
                log.info("Tasks have been COMPLETED. Feel free to Launch the game.")
                return
            if mode== None:
                log.info("Starting TASKs for Normal Patch..")
                def stop_extracting():
                    cls.is_extracting = False

                tasklist = [Exe_Running(), DownloadBEYOND(), UpdateSettings(), Create_Mod_Patch(), Disable_Mods(), stop_extracting()]
                if get_setting("auto-backup") in ["On"]:
                    tasklist.append(backup(cls))
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                ProgressBar.Destroy()

                m = 1.3
                # Kofi button.
                element_1 = cls._frontend.on_canvas.Photo_Image(
                    image_path="support.png",
                    width=int(70* m), height=int(48* m),
                )

                element_2 = cls._frontend.on_canvas.Photo_Image(
                    image_path="support_active.png",
                    width=int(70* m), height=int(48* m),
                )

                element_3 = cls._frontend.on_canvas.Photo_Image(
                    image_path="no_thanks.png",
                    width=int(70* m), height=int(48* m),
                )

                element_4 = cls._frontend.on_canvas.Photo_Image(
                    image_path="no_thanks_active.png",
                    width=int(70* m), height=int(48* m),
                )

                if not cls.os_platform == "Linux":
                    dialog = CustomDialog(cls, "TOTK Optimizer Tasks Completed",
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
                        cls._frontend.open_browser("kofi")

                log.info("Tasks have been COMPLETED. Feel free to Launch the game.")
                return

        def Create_Mod_Patch(mode=None):
            save_user_choices(cls._frontend, cls._frontend.config)

            if mode == "Cheats":
                log.info("Starting Cheat patcher.")
                ProgressBar.string.set("Creating Cheat ManagerPatch.")
                save_user_choices(cls, cls.config, None, "Cheats")
                selected_cheats = {}
                for option_name, option_var in cls.selected_cheats.items():
                    selected_cheats[option_name] = option_var.get()
                # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Legacy together.
                for version_option in cls.cheat_options:
                    version = version_option.get("Version", "")
                    mod_path = os.path.join(cls.load_dir, "Cheat Manager Patch", "cheats")

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
                cls.remove_list.append("Cheat Manager Patch")
                log.info("Applied cheats successfully.")
                return

            elif mode == None:
                log.info("Starting Mod Creator.")
                log.info(f"Generating mod at {cls.load_dir}")
                os.makedirs(cls.load_dir, exist_ok=True)

                # Update progress bar
                ProgressBar.string.set("TOTK Optimizer Patch.")

                # Ensures that the patches are active and ensure that old versions of the mod folder is disabled.
                cls.remove_list.append("!!!TOTK Optimizer")
                cls.add_list.append("Visual Improvements")
                cls.add_list.append("Mod Manager Patch")
                cls.add_list.append("UltraCam")

                ini_file_directory = os.path.join(cls.load_dir, "!!!TOTK Optimizer", "romfs", "UltraCam")
                os.makedirs(ini_file_directory, exist_ok=True)
                ini_file_path = os.path.join(ini_file_directory, "maxlastbreath.ini")

                config = configparser.ConfigParser()
                config.optionxform = lambda option: option
                if os.path.exists(ini_file_path):
                    config.read(ini_file_path)

                ## TOTK UC BEYOND AUTO PATCHER
                patch_info = cls._frontend.ultracam_beyond.get("Keys", [""])
                for patch in cls._frontend.BEYOND_Patches:
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
                    if cls._frontend.BEYOND_Patches[patch] == "auto" or cls._frontend.BEYOND_Patches[patch].get() == "auto":
                        if patch_class.lower() == "dropdown":
                            patch_Names = patch_dict["Values"]
                            config[patch_Config[0]][patch_Config[1]] = str(patch_Names[patch_Default])
                        else:
                            config[patch_Config[0]][patch_Config[1]] = str(patch_Default)
                        continue

                    if patch_class.lower() == "bool" or patch_class.lower() == "scale":
                        config[patch_Config[0]][patch_Config[1]] = cls._frontend.BEYOND_Patches[patch].get()

                    if patch_class.lower() == "dropdown":
                        # exclusive to dropdown.
                        patch_Names = patch_dict["Name_Values"]
                        patch_Values = patch_dict["Values"]
                        index = patch_Names.index(cls._frontend.BEYOND_Patches[patch].get())
                        config[patch_Config[0]][patch_Config[1]] = str(patch_Values[index])

                resolution = cls._frontend.BEYOND_Patches["resolution"].get()
                shadows = int(cls._frontend.BEYOND_Patches["shadow resolution"].get().split("x")[0])

                # ARR = cls._frontend.BEYOND_Patches["aspect ratio"].get().split("x")
                ARR = [16, 9]
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

                if cls.mode == "Legacy":
                    write_Legacy_config(cls._frontend, cls.TOTKconfig, cls._frontend.title_id, "Renderer", "resolution_setup", "2")
                    write_Legacy_config(cls._frontend, cls.TOTKconfig, cls._frontend.title_id, "Core", "memory_layout_mode", f"{layout}")
                    write_Legacy_config(cls._frontend, cls.TOTKconfig, cls._frontend.title_id, "System", "use_docked_mode", "true")

                    if layout > 0:
                        write_Legacy_config(cls._frontend, cls.TOTKconfig, cls._frontend.title_id, "Renderer", "vram_usage_mode", "1")
                    else:
                        write_Legacy_config(cls._frontend, cls.TOTKconfig, cls._frontend.title_id, "Renderer", "vram_usage_mode", "0")

                if cls.mode == "Ryujinx":
                    write_ryujinx_config(cls._frontend, cls.ryujinx_config, "res_scale", 1)
                    if (layout > 0):
                        write_ryujinx_config(cls._frontend, cls.ryujinx_config, "expand_ram", True)
                    else:
                        write_ryujinx_config(cls._frontend, cls.ryujinx_config, "expand_ram", False)

                config["Resolution"]["Width"] = str(New_Resolution[0])
                config["Resolution"]["Height"] = str(New_Resolution[1])

                ## WRITE IN CONFIG FILE FOR UC 2.0
                with open(ini_file_path, 'w+', encoding="utf-8") as configfile:
                    config.write(configfile)


            # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Legacy together.
            try:
                # This logic is disabled with UltraCam Beyond.
                return

                for version_option in cls.version_options:
                    version = version_option.get("version", "")
                    mod_path = os.path.join(cls.load_dir, "Mod Manager Patch", "exefs")

                    # Create the directory if it doesn't exist
                    os.makedirs(mod_path, exist_ok=True)

                    filename = os.path.join(mod_path, f"{version}.pchtxt")
                    all_values = []
                    with open(filename, "w", encoding="utf-8") as file:
                        file.write(version_option.get("Source", "") + "\n")
                        file.write(version_option.get("nsobid", "") + "\n")
                        file.write(version_option.get("offset", "") + "\n")
                        for key, value in version_option.items():
                            if key in cls.ultracam_options.get(
                                    "Skip_Patches"):
                                continue

                            if key not in ["Source", "nsobid", "offset", "version", "Version"] and not cls.selected_options[key].get() == "Off":
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
            ProgressBar.string.set("Creating Settings..")
            if cls._frontend.selected_settings.get() == "No Change":
                ProgressBar.string.set("No Settings Required..")
                return
            if cls.mode == "Legacy":
                setting_preset = cls.Legacy_settings[cls.selected_settings.get()]
                for section in setting_preset:
                    for option in setting_preset[section]:
                        write_Legacy_config(cls, cls.TOTKconfig, cls._frontend.title_id, section, option, str(setting_preset[section][option]))
            ProgressBar.string.set("Finished Creating Settings..")

        def DownloadBEYOND():
            try:
                cls.add_list.append("UltraCam")
                cls.add_list.append("Max DFPS++")
                cls.add_list.append("DFPS")
                link = New_UCBeyond_Download

                Mod_directory = os.path.join(cls.load_dir, "!!!TOTK Optimizer")
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

                ProgressBar.string.set(f"Downloading UltraCam BEYOND")
                log.info(f"Downloading: UltraCam")
                os.makedirs(Mod_directory, exist_ok=True)
                download_unzip(link, Mod_directory)
                log.info(f"Downloaded: UltraCam")
            except Exception as e:
                log.warning(f"FAILED TO DOWNLOAD ULTRACAM BEYOND! {e}")

        def Exe_Running():
            is_Program_Opened = is_process_running(cls.mode + ".exe")
            message = (f"{cls.mode}.exe is Running, \n"
                       f"The Optimizer Requires {cls.mode}.exe to be closed."
                       f"\nDo you wish to close {cls.mode}.exe?")
            if is_Program_Opened is True:
                response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)
                if response is True:
                    subprocess.run(["taskkill", "/F", "/IM", f"{cls.mode}.exe"], check=True)
            if is_Program_Opened is False:
                log.info(f"{cls.mode}.exe is closed, working as expected.")

        def Disable_Mods():
            ProgressBar.string.set(f"Disabling old mods.")
            # Convert the lists to sets, removing any duplicates.
            cls.add_list = set(cls.add_list)
            cls.remove_list = set(cls.remove_list)
            # Run the Main code to Enable and Disable necessary Mods, the remove ensures the mods are enabled.
            if cls.mode == "Legacy":
                for item in cls.add_list:
                    modify_disabled_key(cls.configdir, cls.load_dir, qtconfig, cls._frontend.config_title_id, item, action="add")
                for item in cls.remove_list:
                    modify_disabled_key(cls.configdir, cls.load_dir, qtconfig, cls._frontend.config_title_id, item, action="remove")
            if cls.mode == "Ryujinx" or platform.system() == "Linux" and not cls.is_extracting:
                for item in cls.add_list:
                    item_dir = os.path.join(cls.load_dir, item)
                    if os.path.exists(item_dir):
                        shutil.rmtree(item_dir)
            cls.add_list.clear()
            cls.remove_list.clear()
    
        ProgressBar.Run(cls._window, run_tasks)

    @classmethod
    def select_game_file(command=None):
        # Open a file dialog to browse and select Legacy.exe
        game_path = filedialog.askopenfilename(
            title=f"Please select Tears of The Kingdom Game File.",
            filetypes=[("Nintendo Gamefile", ["*.nsp", "*.xci", "*.NSP", "*.XCI"]), ("All Files", "*.*")]
        )
        if game_path:
            config = configparser.ConfigParser()
            config.read(localconfig, encoding="utf-8")

            if not config.has_section("Paths"):
                config.add_section("Paths")
            config.set("Paths", "game_path", game_path)
        else:
            return
        with open(localconfig, "w", encoding="utf-8") as configfile:
            config.write(configfile, space_around_delimiters=False)
        return game_path

    @classmethod
    def launch_GAME(self):
        config = configparser.ConfigParser()
        config.read(localconfig, encoding="utf-8")
        Game_PATH = config.get("Paths", "game_path", fallback="None")

        if not os.path.exists(Game_PATH):
            log.warning(f"Game not found in {Game_PATH}\n Please select your game file.")
            Game_PATH = self.select_game_file()

        log.info(f"Launching game {Game_PATH}")

        if self.mode == "Legacy":
            mode = "yuzu.exe"
            if is_process_running("yuzu.exe"):
                log.info("Legacy is already running in the background.")
                return

            Legacypath = self.load_Legacy_path(localconfig)
            if os.path.exists(Legacypath):
                Legacy_PATH = Legacypath
            else:
                Legacy_PATH = self.select_Legacy_exe()

            cmd = [f'{Legacy_PATH}', '-u', '1', '-f', '-g', f'{Game_PATH}']

        if self.mode == "Ryujinx":
            mode = "Ryujinx.exe"

            if is_process_running("Ryujinx.exe"):
                log.info("Ryujinx is already running in the background.")
                return

            ryujinx_path = self.load_Legacy_path(localconfig)
            if os.path.exists(ryujinx_path):
                Ryujinx_PATH = ryujinx_path
            else:
                Ryujinx_PATH = self.select_Legacy_exe()
                if Ryujinx_PATH is None: log.warning("Ryujinx wasn't found.")


            cmd = [f'{Ryujinx_PATH}', '-f', f'{Game_PATH}']

        process = subprocess.Popen(cmd, shell=False)