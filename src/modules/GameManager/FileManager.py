from modules.FrontEnd.ProgressBar import ProgressBar
from modules.GameManager.LaunchManager import LaunchManager
from modules.GameManager.ModCreator import ModCreator
from configuration.settings_config import Setting
from modules.TOTK_Optimizer_Modules import *
from configuration.settings import *
from modules.config import *
import ttkbootstrap as ttk
import shutil

class FileManager:

    _window = None
    _frontend = None # Manager class

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
                    if os.path.exists(os.path.join(cls.Globaldir, "load", cls._frontend._patchInfo.ID)):
                        superlog.info(f"Found Legacy Emu folder at: {cls.Globaldir}")
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
                    if os.path.exists(os.path.join(cls.Globaldir, "load", cls._frontend._patchInfo.ID)):
                        superlog.info(f"Found Legacy Emu folder at: {cls.Globaldir}")
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
                cls.load_dir = os.path.join(cls.load_dir, cls._frontend._patchInfo.ID)

                cls.Legacydir = os.path.normpath(os.path.join(home_directory, ".local", "share", "yuzu", "load", cls._frontend._patchInfo.ID))
                return

            if mode == "Ryujinx":
                cls.Globaldir = os.path.join(home_directory, ".config", "Ryujinx")
                flatpak = os.path.join(home_directory, ".var", "app", "org.ryujinx.Ryujinx", "config", "Ryujinx")

                if os.path.exists(flatpak):
                    log.info("Detected a Ryujinx flatpak!")
                    cls.Globaldir = flatpak
                    cls.nand_dir = os.path.join(f"{cls.Globaldir}", "bis", "user", "save")
                    cls.sdmc_dir = os.path.join(f"{cls.Globaldir}", "sdcard")
                    cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", cls._frontend._patchInfo.ID)
                    cls.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents",
                                                cls._frontend._patchInfo.ID)
                    cls.ryujinx_config = os.path.join(cls.Globaldir, "Config.json")
                    return

                cls.configdir = None
                cls.TOTKconfig = None
                cls.nand_dir = os.path.join(f"{cls.Globaldir}", "bis", "user", "save")
                cls.sdmc_dir = os.path.join(f"{cls.Globaldir}", "sdcard")
                cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", cls._frontend._patchInfo.ID)
                cls.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents", cls._frontend._patchInfo.ID)
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
                    if os.path.exists(os.path.join(cls.Globaldir, "load", cls._frontend._patchInfo.ID)):
                        superlog.info(f"Found Legacy Emu folder at: {cls.Globaldir}")
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
                    cls.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{os.path.join(Legacypath, "../user/nand")}')), cls._frontend._patchInfo.ID).replace('"', "")
                    if cls.load_dir.startswith('"'):
                        cls.load_dir = cls.load_dir.strip('"')[0]
                    cls.Legacydir = os.path.join(cls.Globaldir, "load", cls._frontend._patchInfo.ID).replace('"', "")
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
                    cls.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{cls.Globaldir}/load')), cls._frontend._patchInfo.ID).replace('"', "")
                    if cls.load_dir.startswith('"'):
                        cls.load_dir = cls.load_dir.strip('"')[0]
                    cls.Legacydir = os.path.join(cls.Globaldir, "load", cls._frontend._patchInfo.ID)
                    return
            if mode == "Ryujinx":
                if os.path.exists(portablefolder):
                    cls.configdir = None
                    cls.TOTKconfig = None
                    cls.ryujinx_config = os.path.join(portablefolder, "Config.json")
                    cls.nand_dir = os.path.join(f"{portablefolder}", "bis", "user", "save")
                    cls.load_dir = os.path.join(f"{portablefolder}", "mods", "contents", cls._frontend._patchInfo.ID)
                    cls.sdmc_dir = os.path.join(f"{portablefolder}", "sdcard")
                    cls.Legacydir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", cls._frontend._patchInfo.ID)
                    return
                else:
                    cls.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx")
                    cls.configdir = None
                    cls.TOTKconfig = None
                    cls.ryujinx_config = os.path.join(cls.Globaldir, "Config.json")
                    cls.nand_dir = os.path.join(f"{cls.Globaldir}", "bis", "user", "save")
                    cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", cls._frontend._patchInfo.ID)
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
                cls.load_dir = os.path.join(f"{cls.Globaldir}", "mods", "contents", cls._frontend._patchInfo.ID)
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
            superlog.info("Detected a Linux based SYSTEM!")
        elif cls.os_platform == "Windows":
            superlog.info("Detected a Windows based SYSTEM!")
            if mode == "Legacy":
                if os.path.exists(cls.configdir):
                    log.info("a qt-config.ini file found!")
                else:
                    log.warning("qt-config.ini not found, the script will assume default appdata directories, "
                                "please reopen Legacy for consistency and make sure TOTK is present..!")
        elif cls.os_platform == "Darwin":
            log.info("Detected a MacOS based SYSTEM!")

    @classmethod
    def TransferMods(cls):
        patchinfo = cls._frontend._patchInfo
        source = os.path.join(patchinfo.Folder, patchinfo.ModFolder)

        if cls.is_extracting is False:
            destination = os.path.join(cls.Globaldir, "load", patchinfo.ID, patchinfo.ModName)
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else :
            destination = os.path.join(os.getcwd(), patchinfo.ModName)
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)

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
                superlog.info("Starting TASKs for Cheat Patch..")
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
                superlog.info("Tasks have been COMPLETED. Feel free to Launch the game.")
                return
            if mode== None:
                superlog.info("Starting TASKs for Normal Patch..")
                def stop_extracting():
                    cls.is_extracting = False

                tasklist = [Exe_Running(), cls.TransferMods(), UpdateSettings(), Create_Mod_Patch(), Disable_Mods(), stop_extracting()]
                if get_setting("auto-backup") in ["On"]:
                    tasklist.append(backup(cls))
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                
                ProgressBar.End(cls._frontend)
                superlog.info("Tasks have been COMPLETED. Feel free to Launch the game.")
                return

        def Create_Mod_Patch(mode=None):
            save_user_choices(cls._frontend, cls._frontend.config)

            patchInfo = cls._frontend._patchInfo
            modDir = os.path.join(cls.Globaldir, f"load/{patchInfo.ID}")

            if mode == "Cheats":
                ProgressBar.string.set("Creating Cheat Patches.")
                ModCreator.CreateCheats(cls)
                return

            elif mode == None:
                superlog.info("Starting Mod Creator.")
                log.info(f"Generating mod at {modDir}")
                os.makedirs(modDir, exist_ok=True)

                # Update progress bar
                ProgressBar.string.set("TOTK Optimizer Patch.")

                # Ensures that the patches are active and ensure that old versions of the mod folder is disabled.
                cls.remove_list.append(patchInfo.ModName)
                cls.add_list.append("Visual Improvements")
                cls.add_list.append("Mod Manager Patch")
                cls.add_list.append("UltraCam")

                ini_file_path = os.path.join(modDir, patchInfo.ModName, patchInfo.Config)
                if cls.is_extracting: # do this if we are extracting the mod.
                    ini_file_path = os.path.join(os.getcwd(), patchInfo.ModName, patchInfo.Config)
                
                ini_file_directory = os.path.dirname(ini_file_path)
                os.makedirs(ini_file_directory, exist_ok=True)

                config = configparser.ConfigParser()
                config.optionxform = lambda option: option
                if os.path.exists(ini_file_path):
                    config.read(ini_file_path)

                ## TOTK UC BEYOND AUTO PATCHER
                ModCreator.UCAutoPatcher(cls._frontend, config)
                ModCreator.UCResolutionPatcher(cls, cls._frontend, config)

                ## WRITE IN CONFIG FILE FOR UC 2.0
                with open(ini_file_path, 'w+', encoding="utf-8") as configfile:
                    config.write(configfile)

        def UpdateSettings():
            return # return early, this is no longer used but want to keep order of execution.
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

        # Unused Function, used for downloading UltraCam beyond, but no longer needed as we store it locally.
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
            except Exception as e:
                log.warning(f"FAILED TO DOWNLOAD ULTRACAM BEYOND! {e}")

        def Exe_Running():
            is_Program_Opened = LaunchManager.is_process_running(cls._frontend.mode + ".exe")
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