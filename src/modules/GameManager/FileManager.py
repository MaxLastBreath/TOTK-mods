from modules.FrontEnd.ProgressBar import ProgressBar
from modules.GameManager.LaunchManager import LaunchManager
from modules.GameManager.ModCreator import ModCreator
from configuration.settings_config import Setting
from modules.TOTK_Optimizer_Modules import *
from configuration.settings import *
from modules.config import *
import ttkbootstrap as ttk
import subprocess
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
    def Initialize(filemgr, Window, Manager):
        filemgr._frontend = Manager
        filemgr._window = Window

    @classmethod
    def GetClass(filemgr):
        return filemgr

    @classmethod
    def load_Legacy_path(filemgr, config_file):
        if filemgr.mode == "Legacy":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            Legacy_path = config.get('Paths', 'Legacypath', fallback="Appdata")
            return Legacy_path
        if filemgr.mode == "Ryujinx":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            ryujinx_path = config.get('Paths', 'ryujinxpath', fallback="Appdata")
            return ryujinx_path
    
    @classmethod
    def LinuxPaths(filemgr, mode):

        '''Check for Linux Specific Directories...'''

        home_directory = os.path.expanduser("~")

        if mode == "Legacy":
            flatpak = os.path.join(home_directory, ".var", "app", "org.yuzu_emu.yuzu", "config", "yuzu")
            steamdeckdir = os.path.join(home_directory, ".config", "yuzu", "qt-config.ini")

            filemgr.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")
            filemgr.configdir = os.path.join(filemgr.Globaldir, "config", "qt-config.ini")
            filemgr.TOTKconfig = os.path.join(filemgr.Globaldir, "config", "custom")

            # Assume it's a steamdeck
            if os.path.exists(steamdeckdir):
                log.info("Detected a steamdeck!")
                filemgr.configdir = steamdeckdir
                filemgr.TOTKconfig = os.path.join(home_directory, ".config", "yuzu", "custom")

            # Find any "Legacy Emulators"...
            local_dir = os.path.join(home_directory, ".local", "share")
            for folder in os.listdir(local_dir):
                filemgr.Globaldir = os.path.join(local_dir, folder)
                if os.path.exists(os.path.join(filemgr.Globaldir, "load", filemgr._frontend._patchInfo.ID)):
                    superlog.info(f"Found Legacy Emu folder at: {filemgr.Globaldir}")
                    filemgr.configdir = os.path.join(filemgr.Globaldir, "qt-config.ini")
                    filemgr.TOTKconfig = os.path.join(filemgr.Globaldir, "custom")
                    new_path = os.path.dirname(os.path.dirname(filemgr.Globaldir))
                    filemgr.Globaldir = os.path.join(new_path, "data", "yuzu")
                    break
                else:
                    filemgr.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")

            for folder in os.listdir(local_dir):
                filemgr.Globaldir = os.path.join(local_dir, folder, "config", "yuzu")
                if os.path.exists(os.path.join(filemgr.Globaldir, "load", filemgr._frontend._patchInfo.ID)):
                    superlog.info(f"Found Legacy Emu folder at: {filemgr.Globaldir}")
                    filemgr.configdir = os.path.join(filemgr.Globaldir, "qt-config.ini")
                    filemgr.TOTKconfig = os.path.join(filemgr.Globaldir, "custom")
                    new_path = os.path.dirname(os.path.dirname(filemgr.Globaldir))
                    filemgr.Globaldir = os.path.join(new_path, "data", "yuzu")
                    break
                else:
                    filemgr.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")

            config_parser = configparser.ConfigParser()
            config_parser.read(filemgr.configdir, encoding="utf-8")
            filemgr.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{filemgr.Globaldir}/nand')).replace('"', "")
            filemgr.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{filemgr.Globaldir}/sdmc')).replace('"', "")
            if filemgr.nand_dir.startswith('"'):
                filemgr.nand_dir = filemgr.nand_dir.strip('"')[0]
            filemgr.load_dir = os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{filemgr.Globaldir}/load')).replace('"', "")
            if filemgr.nand_dir.startswith('"'):
                filemgr.nand_dir = filemgr.nand_dir.strip('"')[0]
            filemgr.load_dir = os.path.join(filemgr.load_dir, filemgr._frontend._patchInfo.ID)

            filemgr.Legacydir = os.path.normpath(os.path.join(home_directory, ".local", "share", "yuzu", "load", filemgr._frontend._patchInfo.ID))
            return

        if mode == "Ryujinx":
            filemgr.Globaldir = os.path.join(home_directory, ".config", "Ryujinx")
            flatpak = os.path.join(home_directory, ".var", "app", "org.ryujinx.Ryujinx", "config", "Ryujinx")

            if os.path.exists(flatpak):
                log.info("Detected a Ryujinx flatpak!")
                filemgr.Globaldir = flatpak
                filemgr.nand_dir = os.path.join(f"{filemgr.Globaldir}", "bis", "user", "save")
                filemgr.sdmc_dir = os.path.join(f"{filemgr.Globaldir}", "sdcard")
                filemgr.load_dir = os.path.join(f"{filemgr.Globaldir}", "mods", "contents", filemgr._frontend._patchInfo.ID)
                filemgr.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents",
                                            filemgr._frontend._patchInfo.ID)
                filemgr.ryujinx_config = os.path.join(filemgr.Globaldir, "Config.json")
                return

            filemgr.configdir = None
            filemgr.TOTKconfig = None
            filemgr.nand_dir = os.path.join(f"{filemgr.Globaldir}", "bis", "user", "save")
            filemgr.sdmc_dir = os.path.join(f"{filemgr.Globaldir}", "sdcard")
            filemgr.load_dir = os.path.join(f"{filemgr.Globaldir}", "mods", "contents", filemgr._frontend._patchInfo.ID)
            filemgr.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents", filemgr._frontend._patchInfo.ID)
            filemgr.ryujinx_config = os.path.join(filemgr.Globaldir, "Config.json")
            return

    @classmethod
    def WindowsPaths(filemgr, mode):

        '''Check for Windows Specific Directories...'''

        home_directory = os.path.expanduser("~")

        Legacypath = filemgr.load_Legacy_path(localconfig)
        userfolder = os.path.normpath(os.path.join(Legacypath, "../user/"))
        portablefolder = os.path.normpath(os.path.join(Legacypath, "../portable/"))
        
        # Check for user folder
        if mode == "Legacy":
            # Find any "Legacy Emulators"...
            appdata = os.path.join(home_directory, "AppData", "Roaming")
            for folder in os.listdir(appdata):
                filemgr.Globaldir = os.path.join(appdata, folder)
                if os.path.exists(os.path.join(filemgr.Globaldir, "load", filemgr._frontend._patchInfo.ID)):
                    superlog.info(f"Found Legacy Emu folder at: {filemgr.Globaldir}")
                    break
                else:
                    filemgr.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "yuzu")

            if os.path.exists(userfolder):
                filemgr.configdir = os.path.join(Legacypath, "../user/config/qt-config.ini")
                filemgr.TOTKconfig = os.path.join(filemgr.configdir, "../custom")
                config_parser = configparser.ConfigParser()
                config_parser.read(filemgr.configdir, encoding="utf-8")

                filemgr.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{os.path.join(Legacypath, "../user/nand")}')).replace('"', "")
                filemgr.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{os.path.join(Legacypath, "../user/sdmc")}')).replace('"', "")
                
                if filemgr.nand_dir.startswith('"'):
                    filemgr.nand_dir = filemgr.nand_dir.strip('"')[0]

                filemgr.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{os.path.join(Legacypath, "../user/nand")}')), filemgr._frontend._patchInfo.ID).replace('"', "")
                
                if filemgr.load_dir.startswith('"'):
                    filemgr.load_dir = filemgr.load_dir.strip('"')[0]

                filemgr.Legacydir = os.path.join(filemgr.Globaldir, "load", filemgr._frontend._patchInfo.ID).replace('"', "")
                
                NEWLegacy_path = os.path.normpath(os.path.join(userfolder, "../"))
                filemgr.Globaldir = os.path.join(NEWLegacy_path, "user")
                qt_config_save_dir = os.path.normpath(os.path.join(filemgr.nand_dir, "../../"))

                # Warn user that their QT-Config path is INCORRECT!
                if qt_config_save_dir != NEWLegacy_path and filemgr.warn_again == "yes":
                    message = (
                        f"WARNING: Your QT Config Save Directory may not be correct!\n"
                        f"Your saves could be in danger.\n"
                        f"Your current Legacy directory: {NEWLegacy_path}\n"
                        f"Your QT Config Save Directory: {qt_config_save_dir}\n"
                        f"Do you want to create a backup of your save file?"
                    )
                    response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)
                    if response:
                        filemgr.backup()
                        filemgr.warn_again = "no"
                        log.info("Sucessfully backed up save files, in backup folder. "
                                "Please delete qt-config in USER folder! "
                                "Or correct the user folder paths, then use the backup file to recover your saves!")
                        pass
                    else:
                        filemgr.warn_again = "no"
                        log.info("Warning has been declined, "
                                "no saves have been moved!")
                return
            else: # Default to Appdata
                filemgr.configdir = os.path.join(filemgr.Globaldir, "config", "qt-config.ini")
                filemgr.TOTKconfig = os.path.join(filemgr.configdir, "../custom")
                config_parser = configparser.ConfigParser()
                config_parser.read(filemgr.configdir, encoding="utf-8")
                
                filemgr.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{filemgr.Globaldir}/nand')).replace('"', "").replace('"', "")
                filemgr.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{filemgr.Globaldir}/sdmc')).replace('"', "").replace('"', "")
                
                if filemgr.nand_dir.startswith('"'):
                    filemgr.nand_dir = filemgr.nand_dir.strip('"')[0]

                filemgr.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{filemgr.Globaldir}/load')), filemgr._frontend._patchInfo.ID).replace('"', "")
                
                if filemgr.load_dir.startswith('"'):
                    filemgr.load_dir = filemgr.load_dir.strip('"')[0]

                filemgr.Legacydir = os.path.join(filemgr.Globaldir, "load", filemgr._frontend._patchInfo.ID)
                return
            
        if mode == "Ryujinx":
            if os.path.exists(portablefolder):
                filemgr.configdir = None
                filemgr.TOTKconfig = None
                filemgr.ryujinx_config = os.path.join(portablefolder, "Config.json")
                filemgr.nand_dir = os.path.join(f"{portablefolder}", "bis", "user", "save")
                filemgr.load_dir = os.path.join(f"{portablefolder}", "mods", "contents", filemgr._frontend._patchInfo.ID)
                filemgr.sdmc_dir = os.path.join(f"{portablefolder}", "sdcard")
                filemgr.Legacydir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", filemgr._frontend._patchInfo.ID)
                return
            else:
                filemgr.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx")
                filemgr.configdir = None
                filemgr.TOTKconfig = None
                filemgr.ryujinx_config = os.path.join(filemgr.Globaldir, "Config.json")
                filemgr.nand_dir = os.path.join(f"{filemgr.Globaldir}", "bis", "user", "save")
                filemgr.load_dir = os.path.join(f"{filemgr.Globaldir}", "mods", "contents", filemgr._frontend._patchInfo.ID)
                filemgr.sdmc_dir = os.path.join(f"{filemgr.Globaldir}", "sdcard")
                filemgr.Legacydir = filemgr.load_dir
                return

    @classmethod
    def MacOSPaths(filemgr, mode):

        '''Check for MacOS Specific Directories...'''

        home_directory = os.path.expanduser("~")

        if mode == "Ryujinx":
            filemgr.Globaldir = os.path.join(home_directory, "Library", "Application Support", "Ryujinx")
            filemgr.configdir = None
            filemgr.TOTKconfig = None
            filemgr.ryujinx_config = os.path.join(filemgr.Globaldir, "Config.json")
            filemgr.nand_dir = os.path.join(f"{filemgr.Globaldir}", "bis", "user", "save")
            filemgr.sdmc_dir = os.path.join(f"{filemgr.Globaldir}", "sdcard")
            filemgr.load_dir = os.path.join(f"{filemgr.Globaldir}", "mods", "contents", filemgr._frontend._patchInfo.ID)
            filemgr.Legacydir = filemgr.load_dir
            return
        
    @classmethod
    def checkpath(filemgr, mode):

        '''The Primary Logic the TOTK Optimizer uses to find each emulator.'''

        filemgr.os_platform = platform.system()

        if filemgr.os_platform == "Linux":
            filemgr.LinuxPaths(mode)
        
        elif filemgr.os_platform == "Windows":
            filemgr.WindowsPaths(mode)
            
        elif filemgr.os_platform == "Darwin":
            filemgr.MacOSPaths(mode)

        try: # Ensure the path exists.
            # attempt to create qt-config.ini directories in case they don't exist. Give error to warn user
            os.makedirs(filemgr.nand_dir, exist_ok=True)
            os.makedirs(filemgr.load_dir, exist_ok=True)
            os.makedirs(filemgr.Legacydir, exist_ok=True)
        except PermissionError as e:
            log.warrning(f"Unable to create directories, please run {filemgr.mode}, {e}")
            filemgr.warning(f"Unable to create directories, please run {filemgr.mode}, {e}")

    @classmethod
    def DetectOS(filemgr, mode):

        '''Detects the current OS... Used only for Debugging.'''

        if filemgr.os_platform == "Linux":
            superlog.info("Detected a Linux based SYSTEM!")
        elif filemgr.os_platform == "Windows":
            superlog.info("Detected a Windows based SYSTEM!")
            if mode == "Legacy":
                if os.path.exists(filemgr.configdir):
                    log.info("a qt-config.ini file found!")
                else:
                    log.warning("qt-config.ini not found, the script will assume default appdata directories, "
                                "please reopen Legacy for consistency and make sure TOTK is present..!")
        elif filemgr.os_platform == "Darwin":
            log.info("Detected a MacOS based SYSTEM!")

    @classmethod
    def TransferMods(filemgr):

        '''Transfer mod files to the emulator/switch location(s)...'''

        patchinfo = filemgr._frontend._patchInfo
        source = os.path.join(patchinfo.Folder, patchinfo.ModFolder)

        if filemgr.is_extracting is False:
            destination = os.path.join(filemgr.Globaldir, "load", patchinfo.ID, patchinfo.ModName)
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else :
            destination = os.path.join(os.getcwd(), patchinfo.ModName)
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)

    @classmethod
    def backup(filemgr):
        ''' Backup save files for a specific game, for Ryujinx it fetches all games. '''

        if filemgr.mode == "Legacy":
            testforuserdir = os.path.join(filemgr.nand_dir, "user", "save", "0000000000000000")
            target_folder = filemgr._frontend._patchInfo.ID
            GameName = filemgr._frontend._patchInfo.Name

            # checks each individual folder ID for each user and finds the ones with saves for the selected game. Then backups the saves!
            for root, dirs, files in os.walk(testforuserdir):
                if target_folder in dirs:
                    folder_to_backup = os.path.join(root, target_folder)
            print(f"Attemping to backup {folder_to_backup}")

        # Create the 'backup' folder inside the mod manager directory if it doesn't exist
        elif filemgr.mode == "Ryujinx":
            folder_to_backup = filemgr.nand_dir
            
        script_dir = os.path.dirname(os.path.abspath(sys.executable))
        backup_folder_path = os.path.join(script_dir, "backup")
        os.makedirs(backup_folder_path, exist_ok=True)
        backup_file = f"Backup {GameName}_.rar"
        file_number = 1
        while os.path.exists(os.path.join(backup_folder_path, backup_file)):
            backup_file = f"Backup {GameName}_{file_number}.rar"
            file_number += 1

        # Construct the full path for the backup file inside the 'backup' folder
        backup_file_path = os.path.join(backup_folder_path, backup_file)

        try:
            # Check if the folder exists before creating the backup
            if os.path.exists(folder_to_backup):
                shutil.make_archive(backup_file_path, "zip", folder_to_backup)
                os.rename(backup_file_path + ".zip", backup_file_path)
                messagebox.showinfo("Backup", f"Backup created successfully: {backup_file}")
            else:
                messagebox.showerror("Backup Error", "Folder to backup not found.")

        except Exception as e:
            log.error(f"Backup Error", f"Error creating backup: {e}")
            messagebox.showerror("Backup Error", f"Error creating backup: {e}")

    @classmethod
    def clean_shaders(filemgr):
        answer = messagebox.askyesno(title="Legacy Shader Warning.",
                                    message="Are you sure you want to delete your shaders?\n"
                                            "This could Improve performance.")
        emu_dir = filemgr.Globaldir
        if filemgr._frontend.mode == "Legacy":
            shaders = os.path.join(emu_dir, f"shader/{filemgr._frontend._patchInfo.ID}")
        if filemgr._frontend.mode == "Ryujinx":
            shaders = os.path.join(emu_dir, f"games/{filemgr._frontend._patchInfo.ID}/cache/shader")
        if answer is True:
            try:
                shutil.rmtree(shaders)

                log.info("The shaders have been successfully removed")
            except FileNotFoundError as e:
                log.info("No shaders have been found. Potentially already removed.")
        if answer is False:
            log.info("Shaders deletion declined.")

    @classmethod
    def submit(filemgr, mode=None):
        filemgr.add_list = []
        filemgr.remove_list = []
        filemgr.checkpath(mode)
        # Needs to be run after checkpath.
        if filemgr.mode == "Legacy":
            qtconfig = get_config_parser()
            qtconfig.optionxform = lambda option: option
            try:
                qtconfig.read(filemgr.configdir)
            except Exception as e: log.warning(f"Couldn't' find QT-config {e}")
        else:
            qtconfig = None

        def timer(value):
            ProgressBar.progress_bar["value"] = value
            filemgr._window.update_idletasks()

        def run_tasks():
            if mode == "Cheats":
                superlog.info("Starting TASKs for Cheat Patch..")
                tasklist = [Create_Mod_Patch("Cheats")]
                if get_setting("cheat-backup") in ["On"]:
                    tasklist.append(filemgr.backup())
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
                    filemgr.is_extracting = False

                tasklist = [Exe_Running(), filemgr.TransferMods(), UpdateSettings(), Create_Mod_Patch(), Disable_Mods(), stop_extracting()]
                if get_setting("auto-backup") in ["On"]:
                    tasklist.append(filemgr.backup())
                com = 100 // len(tasklist)
                for task in tasklist:
                    timer(com)
                    com += com
                    task
                    time.sleep(0.05)
                
                ProgressBar.End(filemgr._frontend)
                superlog.info("Tasks have been COMPLETED. Feel free to Launch the game.")
                return

        def Create_Mod_Patch(mode=None):
            save_user_choices(filemgr._frontend, filemgr._frontend.config)

            patchInfo = filemgr._frontend._patchInfo
            modDir = os.path.join(filemgr.Globaldir, f"load/{patchInfo.ID}")

            if mode == "Cheats":
                ProgressBar.string.set("Creating Cheat Patches.")
                ModCreator.CreateCheats(filemgr)
                return

            elif mode == None:
                superlog.info("Starting Mod Creator.")
                log.info(f"Generating mod at {modDir}")
                os.makedirs(modDir, exist_ok=True)

                # Update progress bar
                ProgressBar.string.set("TOTK Optimizer Patch.")

                # Ensures that the patches are active and ensure that old versions of the mod folder is disabled.
                filemgr.remove_list.append(patchInfo.ModName)
                filemgr.add_list.append("Visual Improvements")
                filemgr.add_list.append("Mod Manager Patch")
                filemgr.add_list.append("UltraCam")

                ini_file_path = os.path.join(modDir, patchInfo.ModName, patchInfo.Config)
                if filemgr.is_extracting: # do this if we are extracting the mod.
                    ini_file_path = os.path.join(os.getcwd(), patchInfo.ModName, patchInfo.Config)
                
                ini_file_directory = os.path.dirname(ini_file_path)
                os.makedirs(ini_file_directory, exist_ok=True)

                config = configparser.ConfigParser()
                config.optionxform = lambda option: option
                if os.path.exists(ini_file_path):
                    config.read(ini_file_path)

                ## TOTK UC BEYOND AUTO PATCHER
                ModCreator.UCAutoPatcher(filemgr._frontend, config)
                ModCreator.UCResolutionPatcher(filemgr, filemgr._frontend, config)

                ## WRITE IN CONFIG FILE FOR UC 2.0
                with open(ini_file_path, 'w+', encoding="utf-8") as configfile:
                    config.write(configfile)

        def UpdateSettings():
            return # return early, this is no longer used but want to keep order of execution.
            log.info("Checking for Settings...")
            ProgressBar.string.set("Creating Settings..")
            if filemgr._frontend.selected_settings.get() == "No Change":
                ProgressBar.string.set("No Settings Required..")
                return
            if filemgr.mode == "Legacy":
                setting_preset = filemgr.Legacy_settings[filemgr.selected_settings.get()]
                for section in setting_preset:
                    for option in setting_preset[section]:
                        write_Legacy_config(filemgr, filemgr.TOTKconfig, filemgr._frontend.title_id, section, option, str(setting_preset[section][option]))
            ProgressBar.string.set("Finished Creating Settings..")

        # Unused Function, used for downloading UltraCam beyond, but no longer needed as we store it locally.
        def DownloadBEYOND():
            try:
                filemgr.add_list.append("UltraCam")
                filemgr.add_list.append("Max DFPS++")
                filemgr.add_list.append("DFPS")
                link = New_UCBeyond_Download

                Mod_directory = os.path.join(filemgr.load_dir, "!!!TOTK Optimizer")
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
            is_Program_Opened = LaunchManager.is_process_running(filemgr._frontend.mode + ".exe")
            message = (f"{filemgr.mode}.exe is Running, \n"
                       f"The Optimizer Requires {filemgr.mode}.exe to be closed."
                       f"\nDo you wish to close {filemgr.mode}.exe?")
            if is_Program_Opened is True:
                response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)
                if response is True:
                    subprocess.run(["taskkill", "/F", "/IM", f"{filemgr.mode}.exe"], check=True)
            if is_Program_Opened is False:
                log.info(f"{filemgr.mode}.exe is closed, working as expected.")

        def Disable_Mods():
            ProgressBar.string.set(f"Disabling old mods.")
            # Convert the lists to sets, removing any duplicates.
            filemgr.add_list = set(filemgr.add_list)
            filemgr.remove_list = set(filemgr.remove_list)
            # Run the Main code to Enable and Disable necessary Mods, the remove ensures the mods are enabled.
            if filemgr.mode == "Legacy":
                for item in filemgr.add_list:
                    modify_disabled_key(filemgr.configdir, filemgr.load_dir, qtconfig, filemgr._frontend.config_title_id, item, action="add")
                for item in filemgr.remove_list:
                    modify_disabled_key(filemgr.configdir, filemgr.load_dir, qtconfig, filemgr._frontend.config_title_id, item, action="remove")
            if filemgr.mode == "Ryujinx" or platform.system() == "Linux" and not filemgr.is_extracting:
                for item in filemgr.add_list:
                    item_dir = os.path.join(filemgr.load_dir, item)
                    if os.path.exists(item_dir):
                        shutil.rmtree(item_dir)
            filemgr.add_list.clear()
            filemgr.remove_list.clear()
    
        ProgressBar.Run(filemgr._window, run_tasks)