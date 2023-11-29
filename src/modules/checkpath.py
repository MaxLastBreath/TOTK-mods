import os
import platform
import configparser
from modules.logger import *
from configuration.settings import localconfig
from tkinter import messagebox


# Define Directories for different OS or Yuzu Folders, Check if User has correct paths for User Folder.
def checkpath(self, mode):
    home_directory = os.path.expanduser("~")
    # Default Dir for Linux/SteamOS
    self.os_platform = platform.system()
    if self.os_platform == "Linux":
        if mode == "Yuzu":
            flatpak = os.path.join(home_directory, ".var", "app", "org.yuzu_emu.yuzu", "config", "yuzu")
            steamdeckdir = os.path.join(home_directory, ".config", "yuzu", "qt-config.ini")

            self.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")
            self.configdir = os.path.join(self.Globaldir, "config", "qt-config.ini")
            self.TOTKconfig = os.path.join(self.Globaldir, "config", "custom", "0100F2C0115B6000.ini")

            # Assume it's a steamdeck
            if os.path.exists(steamdeckdir):
                log.info("Detected a steamdeck!")
                self.configdir = steamdeckdir
                self.TOTKconfig = os.path.join(home_directory, ".config", "yuzu", "custom", "0100F2C0115B6000.ini")

            # Check for a flatpak.
            if os.path.exists(flatpak):
                log.info("Detected a Yuzu flatpak!")
                self.configdir = os.path.join(flatpak, "qt-config.ini")
                self.TOTKconfig = os.path.join(flatpak, "custom", "0100F2C0115B6000.ini")
                new_path = os.path.dirname(os.path.dirname(flatpak))
                self.Globaldir = os.path.join(new_path, "data", "yuzu")

            config_parser = configparser.ConfigParser()
            config_parser.read(self.configdir)
            self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{self.Globaldir}/nand'))
            self.load_dir = os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{self.Globaldir}/load'))
            self.load_dir = os.path.join(self.load_dir, "0100F2C0115B6000")

            self.Yuzudir = os.path.normpath(os.path.join(home_directory, ".local", "share", "yuzu", "load", "0100F2C0115B6000"))
            return

        if mode == "Ryujinx":
            self.Globaldir = os.path.join(home_directory, ".config", "Ryujinx")
            flatpak = os.path.join(home_directory, ".var", "app", "org.ryujinx.Ryujinx", "config", "Ryujinx")

            if os.path.exists(flatpak):
                log.info("Detected a Ryujinx flatpak!")
                self.Globaldir = flatpak
                self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2c0115b6000")
                self.Yuzudir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents",
                                            "0100f2c0115b6000")
                self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
                return

            self.configdir = None
            self.TOTKconfig = None
            self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
            self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2C0115B6000")
            self.Yuzudir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
            self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
            return
    # Default Dir for Windows or user folder.
    elif self.os_platform == "Windows":
        yuzupath = self.load_yuzu_path(localconfig)
        userfolder = os.path.join(yuzupath, "../user/")
        portablefolder = os.path.join(yuzupath, "../portable/")
        # Check for user folder
        if mode == "Yuzu":
            if os.path.exists(userfolder):
                self.configdir = os.path.join(yuzupath, "../user/config/qt-config.ini")
                self.TOTKconfig = os.path.join(self.configdir, "../custom/0100F2C0115B6000.ini")
                config_parser = configparser.ConfigParser()
                config_parser.read(self.configdir)
                self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{os.path.join(yuzupath, "../user/nand")}'))
                self.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{os.path.join(yuzupath, "../user/nand")}')), "0100F2C0115B6000")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "yuzu", "load", "0100F2C0115B6000")
                NEWyuzu_path = os.path.normpath(os.path.join(userfolder, "../"))
                self.Globaldir = os.path.join(NEWyuzu_path, "user")
                qt_config_save_dir = os.path.normpath(os.path.join(self.nand_dir, "../../"))
                # Warn user that their QT-Config path is INCORRECT!
                if qt_config_save_dir != NEWyuzu_path and self.warn_again == "yes":
                    message = (
                        f"WARNING: Your QT Config Save Directory may not be correct!\n"
                        f"Your saves could be in danger.\n"
                        f"Your current Yuzu directory: {NEWyuzu_path}\n"
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
                self.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "yuzu")
                self.configdir = os.path.join(self.Globaldir, "config", "qt-config.ini")
                self.TOTKconfig = os.path.join(self.configdir, "../custom/0100F2C0115B6000.ini")
                config_parser = configparser.ConfigParser()
                config_parser.read(self.configdir)
                self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{self.Globaldir}/nand'))
                self.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{self.Globaldir}/load')), "0100F2C0115B6000")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "yuzu", "load", "0100F2C0115B6000")
                return
        if mode == "Ryujinx":
            if os.path.exists(portablefolder):
                self.configdir = None
                self.TOTKconfig = None
                self.ryujinx_config = os.path.join(portablefolder, "Config.json")
                self.nand_dir = os.path.join(f"{portablefolder}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{portablefolder}", "mods", "contents", "0100f2C0115b6000")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                return
            else:
                self.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx")
                self.configdir = None
                self.TOTKconfig = None
                self.ryujinx_config = os.path.join(self.Globaldir, "Config.json")
                self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100f2C0115b6000")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100f2C0115B6000")
                return
    # Ensure the path exists.
    try:
        # attempt to create qt-config.ini directories in case they don't exist. Give error to warn user
        os.makedirs(self.nand_dir, exist_ok=True)
        os.makedirs(self.load_dir, exist_ok=True)
        os.makedirs(self.Yuzudir, exist_ok=True)
    except PermissionError as e:
        log.warrning(f"Unable to create directories, please run {self.mode}, {e}")
        self.warning(f"Unable to create directories, please run {self.mode}, {e}")

# Define OS
def DetectOS(self, mode):
    if self.os_platform == "Linux":
        log.info("Detected a Linux based SYSTEM!")
    elif self.os_platform == "Windows":
        log.info("Detected a Windows based SYSTEM!")
        if mode == "Yuzu":
            if os.path.exists(self.configdir):
                log.info("a qt-config.ini file found!")
            else:
                log.warning("qt-config.ini not found, the script will assume default appdata directories, "
                            "please reopen Yuzu for consistency and make sure TOTK is present..!")