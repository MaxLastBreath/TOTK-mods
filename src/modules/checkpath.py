import os
import platform
import configparser
from modules.logger import *
from configuration.settings import localconfig
from tkinter import messagebox
from tkinter import filedialog

# Define Directories for different OS or Legacy Folders, Check if User has correct paths for User Folder.
def checkpath(self, mode):
    if self.is_extracting is True:
        self.configdir = None
        self.TOTKconfig = None
        self.nand_dir = None
        self.ryujinx_config = None
        self.sdmc = None
        self.load_dir = os.getcwd()
        self.Legacydir = os.getcwd()
        self.Globaldir = os.getcwd()
        return

    home_directory = os.path.expanduser("~")
    # Default Dir for Linux/SteamOS
    self.os_platform = platform.system()
    if self.os_platform == "Linux":
        if mode == "Legacy":
            flatpak = os.path.join(home_directory, ".var", "app", "org.Legacy_emu.Legacy", "config", "Legacy")
            steamdeckdir = os.path.join(home_directory, ".config", "Legacy", "qt-config.ini")

            self.Globaldir = os.path.join(home_directory, ".local", "share", "Legacy")
            self.configdir = os.path.join(self.Globaldir, "config", "qt-config.ini")
            self.TOTKconfig = os.path.join(self.Globaldir, "config", "custom")

            # Assume it's a steamdeck
            if os.path.exists(steamdeckdir):
                log.info("Detected a steamdeck!")
                self.configdir = steamdeckdir
                self.TOTKconfig = os.path.join(home_directory, ".config", "Legacy", "custom")

            # Check for a flatpak.
            if os.path.exists(flatpak):
                log.info("Detected a Legacy flatpak!")
                self.configdir = os.path.join(flatpak, "qt-config.ini")
                self.TOTKconfig = os.path.join(flatpak, "custom")
                new_path = os.path.dirname(os.path.dirname(flatpak))
                self.Globaldir = os.path.join(new_path, "data", "Legacy")

            config_parser = configparser.ConfigParser()
            config_parser.read(self.configdir, encoding="utf-8")
            self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{self.Globaldir}/nand'))
            self.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{self.Globaldir}/sdmc'))
            if self.nand_dir.startswith('"'):
                self.nand_dir = self.nand_dir.strip('"')[0]
            self.load_dir = os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{self.Globaldir}/load'))
            if self.nand_dir.startswith('"'):
                self.nand_dir = self.nand_dir.strip('"')[0]
            self.load_dir = os.path.join(self.load_dir, "0100F2C0115B6000")

            self.Legacydir = os.path.normpath(os.path.join(home_directory, ".local", "share", "Legacy", "load", "0100F2C0115B6000"))
            return

        if mode == "Ryujinx":
            self.Globaldir = os.path.join(home_directory, ".config", "Ryujinx")
            flatpak = os.path.join(home_directory, ".var", "app", "org.ryujinx.Ryujinx", "config", "Ryujinx")

            if os.path.exists(flatpak):
                log.info("Detected a Ryujinx flatpak!")
                self.Globaldir = flatpak
                self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
                self.sdmc_dir = os.path.join(f"{self.Globaldir}", "sdcard")
                self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2c0115b6000")
                self.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents",
                                            "0100f2c0115b6000")
                self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
                return

            self.configdir = None
            self.TOTKconfig = None
            self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
            self.sdmc_dir = os.path.join(f"{self.Globaldir}", "sdcard")
            self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2C0115B6000")
            self.Legacydir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
            self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
            return
    # Default Dir for Windows or user folder.
    elif self.os_platform == "Windows":
        Legacypath = load_Legacy_path(self, localconfig)
        userfolder = os.path.normpath(os.path.join(Legacypath, "../user/"))
        portablefolder = os.path.normpath(os.path.join(Legacypath, "../portable/"))
        # Check for user folder
        if mode == "Legacy":
            # Find any "Legacy Emulators"...
            appdata = os.path.join(home_directory, "AppData", "Roaming")
            for folder in os.listdir(appdata):
                self.Globaldir = os.path.join(appdata, folder)
                if os.path.exists(os.path.join(self.Globaldir, "load", "0100F2C0115B6000")):
                    print(f"Found Legacy Emu folder at: {self.Globaldir}")
                    break
                else:
                    self.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "yuzu")

            if os.path.exists(userfolder):
                self.configdir = os.path.join(Legacypath, "../user/config/qt-config.ini")
                self.TOTKconfig = os.path.join(self.configdir, "../custom")
                config_parser = configparser.ConfigParser()
                config_parser.read(self.configdir, encoding="utf-8")
                self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{os.path.join(Legacypath, "../user/nand")}'))
                self.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{os.path.join(Legacypath, "../user/sdmc")}'))
                if self.nand_dir.startswith('"'):
                    self.nand_dir = self.nand_dir.strip('"')[0]
                self.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{os.path.join(Legacypath, "../user/nand")}')), "0100F2C0115B6000")
                if self.load_dir.startswith('"'):
                    self.load_dir = self.load_dir.strip('"')[0]
                self.Legacydir = os.path.join(self.Globaldir, "load", "0100F2C0115B6000")
                NEWLegacy_path = os.path.normpath(os.path.join(userfolder, "../"))
                self.Globaldir = os.path.join(NEWLegacy_path, "user")
                qt_config_save_dir = os.path.normpath(os.path.join(self.nand_dir, "../../"))
                # Warn user that their QT-Config path is INCORRECT!
                if qt_config_save_dir != NEWLegacy_path and self.warn_again == "yes":
                    message = (
                        f"WARNING: Your QT Config Save Directory may not be correct!\n"
                        f"Your saves could be in danger.\n"
                        f"Your current Legacy directory: {NEWLegacy_path}\n"
                        f"Your QT Config Save Directory: {qt_config_save_dir}\n"
                        f"Do you want to create a backup of your save file?"
                    )
                    response = messagebox.askyesno("Warning", message, icon=messagebox.WARNING)
                    if response:
                        self.backup()
                        self.warn_again = "no"
                        log.info("Sucessfully backed up save files, in backup folder. "
                                 "Please delete qt-config in USER folder! "
                                 "Or correct the user folder paths, then use the backup file to recover your saves!")
                        pass
                    else:
                        self.warn_again = "no"
                        log.info("Warning has been declined, "
                                 "no saves have been moved!")
                return
            # Default to Appdata
            else:
                self.configdir = os.path.join(self.Globaldir, "config", "qt-config.ini")
                self.TOTKconfig = os.path.join(self.configdir, "../custom")
                config_parser = configparser.ConfigParser()
                config_parser.read(self.configdir, encoding="utf-8")
                self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{self.Globaldir}/nand'))
                self.sdmc_dir = os.path.normpath(config_parser.get('Data%20Storage', 'sdmc_directory', fallback=f'{self.Globaldir}/sdmc'))
                if self.nand_dir.startswith('"'):
                    self.nand_dir = self.nand_dir.strip('"')[0]
                self.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{self.Globaldir}/load')), "0100F2C0115B6000")
                if self.load_dir.startswith('"'):
                    self.load_dir = self.load_dir.strip('"')[0]
                self.Legacydir = os.path.join(self.Globaldir, "load", "0100F2C0115B6000")


                return
        if mode == "Ryujinx":
            if os.path.exists(portablefolder):
                self.configdir = None
                self.TOTKconfig = None
                self.ryujinx_config = os.path.join(portablefolder, "Config.json")
                self.nand_dir = os.path.join(f"{portablefolder}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{portablefolder}", "mods", "contents", "0100f2C0115b6000")
                self.sdmc_dir = os.path.join(f"{portablefolder}", "sdcard")
                self.Legacydir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                return
            else:
                self.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx")
                self.configdir = None
                self.TOTKconfig = None
                self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
                self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2C0115b6000")
                self.sdmc_dir = os.path.join(f"{self.Globaldir}", "sdcard")
                self.Legacydir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                return
    # Ensure the path exists.
    try:
        # attempt to create qt-config.ini directories in case they don't exist. Give error to warn user
        os.makedirs(self.nand_dir, exist_ok=True)
        os.makedirs(self.load_dir, exist_ok=True)
        os.makedirs(self.Legacydir, exist_ok=True)
    except PermissionError as e:
        log.warrning(f"Unable to create directories, please run {self.mode}, {e}")
        self.warning(f"Unable to create directories, please run {self.mode}, {e}")

# Define OS
def DetectOS(self, mode):
    if self.os_platform == "Linux":
        log.info("Detected a Linux based SYSTEM!")
    elif self.os_platform == "Windows":
        log.info("Detected a Windows based SYSTEM!")
        if mode == "Legacy":
            if os.path.exists(self.configdir):
                log.info("a qt-config.ini file found!")
            else:
                log.warning("qt-config.ini not found, the script will assume default appdata directories, "
                            "please reopen Legacy for consistency and make sure TOTK is present..!")

def load_Legacy_path(self, config_file):
    if self.mode == "Legacy":
        config = configparser.ConfigParser()
        config.read(config_file, encoding="utf-8")
        Legacy_path = config.get('Paths', 'Legacypath', fallback="Appdata")
        return Legacy_path
    if self.mode == "Ryujinx":
        config = configparser.ConfigParser()
        config.read(config_file, encoding="utf-8")
        ryujinx_path = config.get('Paths', 'ryujinxpath', fallback="Appdata")
        return ryujinx_path