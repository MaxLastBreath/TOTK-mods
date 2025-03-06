from __future__ import annotations
import time
from modules.FrontEnd.ProgressBar import ProgressBar
from modules.GameManager.LaunchManager import LaunchManager
from modules.GameManager.ModCreator import ModCreator
from modules.TOTK_Optimizer_Modules import *
from configuration.settings import *
from modules.config import *
import ttkbootstrap as ttk
import subprocess
import shutil
from tkinter import simpledialog

import tkinter as tk
from tkinter import messagebox

class FileManager:

    _window: ttk.Window = None
    _manager: any = None
    _emu_blacklist = ["citra-emu", "lime3ds-emu"]

    home_directory = os.path.expanduser("~")
    os_platform = platform.system()

    is_extracting = False

    _emuglobal: str = None
    _emuconfig: str = None
    _gameconfig: str = None
    nand: str = None
    sdmc: str = None
    load: str = None
    contentID: str = None

    @classmethod
    # Initialize our Window here.
    def Initialize(filemgr, Window, Mgr):
        from modules.FrontEnd.FrontEnd import Manager  # avoid Circular Imports.

        filemgr._manager : Manager = Mgr
        filemgr._window = Window

    @classmethod
    # fmt: off
    def Warn_LegacySaves(filemgr, OldPath, NewPath):
        message = (
            f"WARNING: Your QT Config Save Directory may not be correct!\n"
            f"Your saves could be in danger.\n"
            f"Your current Legacy directory: {NewPath}\n"
            f"Your QT Config Save Directory: {OldPath}\n"
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
    
    @classmethod
    # fmt: off
    def load_Legacy_path(filemgr, config_file: str):
        if filemgr._manager.mode == "Legacy":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            Legacy_path = config.get('Paths', 'Legacypath', fallback="Appdata")
            return Legacy_path
        if filemgr._manager.mode == "Ryujinx":
            config = configparser.ConfigParser()
            config.read(config_file, encoding="utf-8")
            ryujinx_path = config.get('Paths', 'ryujinxpath', fallback="Appdata")
            return ryujinx_path

    @classmethod
    # fmt: off
    def LoopSearch(filemgr) -> str:
        GameID = filemgr._manager._patchInfo.ID

        EmuList = []

        if (filemgr.os_platform == "Windows"):
            SpecialDir = "AppData/Roaming"
        elif filemgr.os_platform == "Linux":
            SpecialDir = ".local/share"

        userDir = os.path.join(filemgr.home_directory, SpecialDir)
        for folder in os.listdir(userDir):
            base_directory = os.path.join(userDir, folder)
            if os.path.exists(os.path.join(base_directory, "load", GameID)):
                EmuList.append(base_directory)
                superlog.info(f"Found Legacy Emu folder at: {base_directory}")
                continue
            if len(EmuList) < 1: # Fallback to citron
                base_directory = os.path.join(filemgr.home_directory, SpecialDir, "citron")

        return base_directory
    
    @classmethod
    # fmt: off
    def LoopSearchLinuxConfig(filemgr) -> str:
        SpecialDir = ".config"
        userDir = os.path.join(filemgr.home_directory, SpecialDir)

        for folder in os.listdir(userDir):

            if folder in filemgr._emu_blacklist:
                continue

            base_directory = os.path.join(userDir, folder)
            lookupfile = os.path.join(base_directory, "qt-config.ini")

            if os.path.exists(lookupfile):
                log.info(f"Found Config File {lookupfile}")
                return lookupfile
            
        return None
        
    @classmethod
    # fmt: off
    def PopulateRyujinx(filemgr):
        patchinfo = filemgr._manager._patchInfo
        portablefolder = os.path.normpath(os.path.join(filemgr.load_Legacy_path(localconfig), "..", "portable/"))

        base_directory = filemgr.home_directory
        if (filemgr.os_platform == "Windows"):
            base_directory = os.path.join(filemgr.home_directory, "AppData", "Roaming", "Ryujinx")
        elif filemgr.os_platform == "Darwin":
            base_directory = os.path.join(filemgr.home_directory, "Library", "Application Support", "Ryujinx")
        if filemgr.os_platform == "Linux":
            base_directory = os.path.join(filemgr.home_directory, ".config", "Ryujinx")
            flatpak = os.path.join(filemgr.home_directory, ".var", "app", "org.ryujinx.Ryujinx", "config", "Ryujinx")
            if(os.path.exists(flatpak)):
                base_directory = flatpak
        if (os.path.exists(portablefolder)):
            base_directory = portablefolder

        filemgr._emuglobal = base_directory
        filemgr._emuconfig = os.path.join(base_directory, "Config.json")
        filemgr.nand = os.path.join(base_directory, "bis", "user", "save")
        filemgr.load = os.path.join(base_directory, "mods", "contents")
        filemgr.sdmc_dir = os.path.join(base_directory, "sdcard")
        filemgr.contentID = os.path.join(base_directory, "mods", "contents", patchinfo.ID)
        filemgr._gameconfig = os.path.join(base_directory, "games", f"{patchinfo.ID}", "Config.json")
    
    @classmethod
    # fmt: off
    def PopulateLegacy(filemgr):
        portablefolder = os.path.normpath(os.path.join(filemgr.load_Legacy_path(localconfig), "..", "user/"))

        base_directory = filemgr.home_directory
        patchinfo = filemgr._manager._patchInfo

        base_directory = filemgr.LoopSearch()

        if (os.path.exists(portablefolder)):
            base_directory = portablefolder

        # Config FIle BS
        if (filemgr.os_platform == "Linux"):
            filemgr._emuconfig = filemgr.LoopSearchLinuxConfig()
        else:
            filemgr._emuconfig = os.path.join(base_directory, "config/qt-config.ini")

        filemgr._emuglobal = base_directory
        filemgr.nand = os.path.join(base_directory, "nand")
        filemgr.load = os.path.join(base_directory, "load")
        filemgr.sdmc_dir = os.path.join(base_directory, "sdmc")

        if os.path.exists(filemgr._emuconfig):
            config_parser = configparser.ConfigParser()
            config_parser.read(filemgr._emuconfig, encoding="utf-8")
        
            NEW_nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=filemgr.nand)).replace('"', "")
            filemgr.load = os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=filemgr.load)).replace('"', "")
            filemgr.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=filemgr.sdmc)).replace('"', "")

            if (os.path.exists(portablefolder) and NEW_nand_dir is not filemgr.nand and filemgr.warn_again == "yes"):
                filemgr.Warn_LegacySaves()
            filemgr.nand = NEW_nand_dir

        filemgr.contentID = os.path.join(filemgr.load, patchinfo.ID)
        filemgr._gameconfig = os.path.join(filemgr._emuconfig, "..", "custom")

    @classmethod
    # fmt: off
    def checkpath(filemgr, mode:str):

        '''The Primary Logic the TOTK Optimizer uses to find each emulator.'''

        # Populate Paths for Emulators
        if mode == "Legacy":
            filemgr.PopulateLegacy()
        if mode == "Ryujinx":
            filemgr.PopulateRyujinx()

        try: # Ensure the path exists.
            # attempt to create qt-config.ini directories in case they don't exist. Give error to warn user
            os.makedirs(filemgr.nand, exist_ok=True)
            os.makedirs(filemgr.load, exist_ok=True)
            os.makedirs(filemgr.contentID, exist_ok=True)
        except PermissionError as e:
            log.warrning(f"Unable to create directories, please run {filemgr._manager.mode}, {e}")
            filemgr.warning(f"Unable to create directories, please run {filemgr._manager.mode}, {e}")

    @classmethod
    def DetectOS(filemgr, mode: str):
        """Detects the current OS... Used only for Debugging."""

        if filemgr.os_platform == "Linux":
            superlog.info("Detected a Linux based SYSTEM!")
        elif filemgr.os_platform == "Windows":
            superlog.info("Detected a Windows based SYSTEM!")
            if mode == "Legacy":
                if os.path.exists(filemgr._emuconfig):
                    log.info("a qt-config.ini file found!")
                else:
                    log.warning(
                        "qt-config.ini not found, the script will assume default appdata directories, "
                        "please reopen Legacy for consistency and make sure TOTK is present..!"
                    )
        elif filemgr.os_platform == "Darwin":
            log.info("Detected a MacOS based SYSTEM!")

    @classmethod
    def TransferMods(filemgr):
        """Transfer mod files to the emulator/switch location(s)..."""

        patchinfo = filemgr._manager._patchInfo
        source = patchinfo.GetModPath()

        if filemgr.is_extracting is False:
            destination = os.path.join(filemgr.contentID, patchinfo.ModName)
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            destination = os.path.join(os.getcwd(), patchinfo.ModName)
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)

        log.info(f"Copying Mod Folder. {source} to {destination}")

    @classmethod
    def backup(filemgr):
        """Backup save files for a specific game, for Ryujinx it fetches all games."""

        if filemgr._manager.mode == "Legacy":
            testforuserdir = os.path.join(
                filemgr.nand, "user", "save", "0000000000000000"
            )
            target_folder = filemgr._manager._patchInfo.ID
            GameName = filemgr._manager._patchInfo.Name

            try:
                # checks each individual folder ID for each user and finds the ones with saves for the selected game. Then backups the saves!
                for root, dirs, files in os.walk(testforuserdir):
                    if target_folder in dirs:
                        folder_to_backup = os.path.join(root, target_folder)
                print(f"Attemping to backup {folder_to_backup}")
            except UnboundLocalError as e:
                log.error("No Folder to backup Found.")
                return

        # Create the 'backup' folder inside the mod manager directory if it doesn't exist
        elif filemgr._manager.mode == "Ryujinx":
            folder_to_backup = filemgr.nand

        local_dir = os.path.dirname(os.path.abspath(sys.executable))
        backup_folder_path = os.path.join(local_dir, "backup")

        try:
            os.makedirs(backup_folder_path, exist_ok=True)
        except PermissionError as e:
            log.error(
                f"The Optimizer doesn't have permission to create or copy folders, please move it to a different location then {os.getcwd()}"
            )
            return

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
                messagebox.showinfo(
                    "Backup", f"Backup created successfully: {backup_file}"
                )
            else:
                messagebox.showerror("Backup Error", "Folder to backup not found.")

        except Exception as e:
            log.error(f"Backup Error", f"Error creating backup: {e}")
            messagebox.showerror("Backup Error", f"Error creating backup: {e}")

    @classmethod
    def clean_shaders(filemgr):
        answer = messagebox.askyesno(
            title="Legacy Shader Warning.",
            message="Are you sure you want to delete your shaders?\n"
            "This could Improve performance.",
        )
        emu_dir = filemgr._emuglobal
        if filemgr._manager.mode == "Legacy":
            shaders = os.path.join(emu_dir, f"shader/{filemgr._manager._patchInfo.ID}")
        if filemgr._manager.mode == "Ryujinx":
            shaders = os.path.join(
                emu_dir, f"games/{filemgr._manager._patchInfo.ID}/cache/shader"
            )
        if answer is True:
            try:
                shutil.rmtree(shaders)

                log.info("The shaders have been successfully removed")
            except FileNotFoundError as e:
                log.info("No shaders have been found. Potentially already removed.")
        if answer is False:
            log.info("Shaders deletion declined.")

    @classmethod
    def UltraCam_ConfigPath(filemgr) -> str:
        PatchInfo = filemgr._manager._patchInfo
        SdCard = filemgr.sdmc_dir

        if filemgr.is_extracting is True:
            Folder = os.path.join(os.getcwd(), "Extracted Files")
            os.makedirs(Folder, exist_ok=True)
            return os.path.join(Folder, PatchInfo.ModName, PatchInfo.Config)
        
        if PatchInfo.SDCardConfig is True:
            return os.path.join(SdCard, PatchInfo.Config)
        else:
            return os.path.join(filemgr.contentID, PatchInfo.ModName, PatchInfo.Config)

    @classmethod
    def submit(filemgr, mode: str | None = None):

        superlog.info(f"STARTING {mode}")

        filemgr.add_list = []
        filemgr.remove_list = []

        def timer(value):
            ProgressBar.progress_bar["value"] = value
            filemgr._window.update_idletasks()

        def run_tasklists(tasklist):
            com = 100 // len(tasklist)
            for task in tasklist:
                timer(com)
                com += com
                task
                time.sleep(0.05)

            ProgressBar.End(filemgr._manager)

        def run_tasks():
            if mode == "Cheats":
                superlog.info("Starting TASKs for Cheat Patch..")
                tasklist = [Create_Mod_Patch("Cheats")]

                if get_setting("cheat-backup") in ["On"]:
                    tasklist.append(filemgr.backup())

                run_tasklists(tasklist)

                superlog.info(
                    "Tasks have been COMPLETED. Feel free to Launch the game."
                )
                return
            if mode == None:
                superlog.info("Starting TASKs for Normal Patch..")

                def stop_extracting():
                    filemgr.is_extracting = False

                tasklist = [
                    Exe_Running(),
                    filemgr.TransferMods(),
                    Create_Mod_Patch(),
                    Disable_Mods(),
                    stop_extracting(),
                ]

                if get_setting("auto-backup") in ["On"]:
                    tasklist.append(filemgr.backup())
                
                run_tasklists(tasklist)

                ProgressBar.End(filemgr._manager)
                superlog.info(
                    "Tasks have been COMPLETED. Feel free to Launch the game."
                )
                return

        def Create_Mod_Patch(mode: str | None = None):
            save_user_choices(filemgr._manager, filemgr._manager.config)

            patchInfo = filemgr._manager._patchInfo
            modDir = filemgr.contentID
            modName = filemgr._manager._patchInfo.ModName

            if mode == "Cheats":
                ProgressBar.string.set("Creating Cheat Patches.")
                ModCreator.CreateCheats()
                return

            elif mode == None:
                log.info(f"Generating mod at {modDir}")
                os.makedirs(modDir, exist_ok=True)

                # Update progress bar
                ProgressBar.string.set("NX-Optimizer Patching...")

                # Ensures that the patches are active and ensure that old versions of the mod folder is disabled.
                filemgr.remove_list.append(modName)
                filemgr.add_list.append("Visual Improvements")
                filemgr.add_list.append("Mod Manager Patch")
                filemgr.add_list.append("UltraCam")

                ini_file_path = filemgr.UltraCam_ConfigPath()

                log.warning(f"Creating {modName} config File Path... {ini_file_path}\n")

                ini_file_directory = os.path.dirname(ini_file_path)
                os.makedirs(ini_file_directory, exist_ok=True)

                log.info(f"Opening {modName} config file...")

                config = configparser.ConfigParser()
                config.optionxform = lambda option: option
                if os.path.exists(ini_file_path):
                    config.read(ini_file_path, encoding="utf-8")

                log.info(f"Starting {modName} Patcher...")

                ## TOTK UC BEYOND AUTO PATCHER
                ModCreator.UCAutoPatcher(filemgr._manager, config)
                ModCreator.UCResolutionPatcher(filemgr, filemgr._manager, config)
                ModCreator.UCAspectRatioPatcher(filemgr._manager, config)

                log.info(f"Starting {modName} Patcher has finished running...")

                ## WRITE IN CONFIG FILE FOR UC 2.0
                with open(ini_file_path, "w+", encoding="utf-8") as configfile:
                    config.write(configfile)

        def Exe_Running():

            if (filemgr.os_platform != "Windows"):
                log.info("Platform is not Windows, No need to check for Executable running.")
                return
            
            is_Program_Opened = LaunchManager.is_process_running(
                filemgr._manager.mode + ".exe"
            )

            message = (
                f"{filemgr._manager.mode}.exe is Running, \n"
                f"The Optimizer Requires {filemgr._manager.mode}.exe to be closed."
                f"\nDo you wish to close {filemgr._manager.mode}.exe?"
            )
            if is_Program_Opened is True:
                response = messagebox.askyesno(
                    "Warning", message, icon=messagebox.WARNING
                )
                if response is True:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", f"{filemgr._manager.mode}.exe"],
                        check=True,
                    )
            if is_Program_Opened is False:
                log.info(f"{filemgr._manager.mode}.exe is closed, working as expected.")

        def Disable_Mods():
            ProgressBar.string.set(f"Disabling old mods...")
            log.info("Disabling Outdated Mods...")
            # Convert the lists to sets, removing any duplicates.
            filemgr.add_list = set(filemgr.add_list)
            filemgr.remove_list = set(filemgr.remove_list)
            # Run the Main code to Enable and Disable necessary Mods, the remove ensures the mods are enabled.
            if filemgr._manager.mode == "Legacy":
                
                # read config to pass into disabled keys h
                emuconfig = configparser.ConfigParser()
                emuconfig.read(filemgr._emuconfig, encoding="utf-8")

                for item in filemgr.add_list:
                    modify_disabled_key(
                        filemgr._emuconfig,
                        filemgr.contentID,
                        emuconfig,
                        filemgr._manager._patchInfo.IDtoNum(),
                        item,
                        action="add",
                    )

                for item in filemgr.remove_list:
                    modify_disabled_key(
                        filemgr._emuconfig,
                        filemgr.contentID,
                        emuconfig,
                        filemgr._manager._patchInfo.IDtoNum(),
                        item,
                        action="remove",
                    )

            # fmt: off
            if (filemgr._manager.mode == "Ryujinx" or platform.system() == "Linux" and not filemgr.is_extracting):
                for item in filemgr.add_list:
                    log.error(f"NOT IMPLEMENTED RYUJINX LOOP {item}")
            filemgr.add_list.clear()
            filemgr.remove_list.clear()

        ProgressBar.Run(filemgr._window, run_tasks)
