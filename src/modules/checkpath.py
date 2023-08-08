import os
import platform
import configparser
from tkinter import messagebox


# Define Directories for different OS or Yuzu Folders, Check if User has correct paths for User Folder.
def checkpath(self, mode):
    home_directory = os.path.expanduser("~")
    # Default Dir for Linux/SteamOS
    self.os_platform = platform.system()
    if self.os_platform == "Linux":
        if mode == "Yuzu":
            self.Globaldir = os.path.join(home_directory, ".local", "share", "yuzu")
            self.configdir = os.path.join(self.Globaldir, "config", "qt-config.ini")
            self.TOTKconfig = os.path.join(self.Globaldir, "config", "custom", "0100F2C0115B6000.ini")
            if not os.path.exists(self.configdir):
                print("Detected a steamdeck!")
                self.configdir = os.path.join(home_directory, ".config", "yuzu", "qt-config.ini")
                self.TOTKconfig = os.path.join(home_directory, ".config", "yuzu", "custom", "0100F2C0115B6000.ini")
            config_parser = configparser.ConfigParser()
            config_parser.read(self.configdir)
            self.nand_dir = os.path.normpath(config_parser.get('Data%20Storage', 'nand_directory', fallback=f'{self.Globaldir}/nand'))
            self.load_dir = os.path.join(os.path.normpath(config_parser.get('Data%20Storage', 'load_directory', fallback=f'{self.Globaldir}/load')), "0100F2C0115B6000")
            self.Yuzudir = os.path.join(home_directory, ".local", "share", "yuzu", "load", "0100F2C0115B6000")
        if mode == "Ryujinx":
            self.Globaldir = os.path.join(home_directory, ".config", "Ryujinx")
            self.configdir = None
            self.TOTKconfig = None
            self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
            self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100F2C0115B6000")
            self.Yuzudir = os.path.join(home_directory, ".config", "Ryujinx", "mods", "contents", "0100F2C0115B6000")
    # Default Dir for Windows or user folder.
    elif self.os_platform == "Windows":
        config = "VisualImprovements.ini"
        yuzupath = self.load_yuzu_path(config)
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
                qt_config_save_dir = os.path.normpath(os.path.join(self.nand_dir, "../../"))
                # Warn user that their QT-Config path is INCORRECT!
                if qt_config_save_dir != NEWyuzu_path and self.warnagain == "yes":
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
                        self.warnagain = "no"
                        print("Sucessfully backed up save files, in backup folder. Please delete qt-config in USER folder! Or correct the user folder paths, then use the backup file to recover your saves!")
                        pass
                    else:
                        self.warnagain = "no"
                        print("Warning has been declined!")
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
                print("Found portable Folder")
                self.configdir = None
                self.TOTKconfig = None
                self.nand_dir = os.path.join(f"{portablefolder}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{portablefolder}", "mods", "contents", "0100F2C0115B6000")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100F2C0115B6000")
            else:
                print("Ryujinx Mode selected!")
                self.Globaldir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx")
                self.configdir = None
                self.TOTKconfig = None
                self.nand_dir = os.path.join(f"{self.Globaldir}", "bis", "user", "save")
                self.load_dir = os.path.join(f"{self.Globaldir}", "mods", "contents", "0100F2C0115B6000")
                self.Yuzudir = os.path.join(home_directory, "AppData", "Roaming", "Ryujinx", "mods", "contents", "0100F2C0115B6000")
    # Ensure the path exists.
    if self.os_platform == "Windows":
        # Ensure directories exist for windows, skip for linux (gives off permission errors.)
        os.makedirs(self.nand_dir, exist_ok=True)
        os.makedirs(self.load_dir, exist_ok=True)
        os.makedirs(self.Yuzudir, exist_ok=True)

# Define OS
def DetectOS(self, mode):
    if self.os_platform == "Linux":
        print("Detected a Linux based SYSTEM!")
    elif self.os_platform == "Windows":
        print("Detected a Windows based SYSTEM!")
        if mode == "Yuzu":
            if os.path.exists(self.configdir):
                print("a qt-config.ini file found!")
            else:
                print("qt-config.ini not found, the script will assume default appdata directories, please reopen Yuzu for consistency and make sure TOTK is present..!")