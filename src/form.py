import tkinter as tk
from tkinter import CURRENT, Tk, ttk, filedialog, messagebox, Toplevel
import configparser
import threading
import os
import sys
import shutil
import patoolib
import json
import requests
import tkinter.font as tkFont
import platform
from PIL import Image, ImageTk
from datetime import datetime, timezone
from configparser import NoOptionError
from pathlib import Path
import time

class Manager:
    def __init__(self, window):
        # Variables
        self.config = "VisualImprovements.ini"
        self.Yuzudir = None
        self.warnagain = "yes"
        self.root = window
        self.window = window
        # Run Script
        self.checkpath()
        self.DetectOS()
        # Load options from DFPS.json
        self.dfps_options = self.load_dfps_options_from_json()
        # Load options from Version.json
        self.version_options = self.load_version_options_from_json()
        self.scalingfactor = 1
        # Create the main canvas
        canvas = tk.Canvas(window, width=1200 * self.scalingfactor, height=600 * self.scalingfactor)
        canvas.pack()
        # Configure Text Font.
        textfont = ("Arial Bold", 10, "bold")
        # Create a transparent black background
        UI_path = self.get_UI_path("BG_Left.png")
        image = Image.open(UI_path)
        image = image.resize((1200 * self.scalingfactor, 600 * self.scalingfactor))
        self.background_UI = ImageTk.PhotoImage(image)
        UI_path2 = self.get_UI_path("BG_Right.png")
        image = Image.open(UI_path2)
        image = image.resize((1200, 600))
        self.background_UI2 = ImageTk.PhotoImage(image)
        # Load and set the image as the background
        image_path = self.get_UI_path("image.png")
        image = Image.open(image_path)
        image = image.resize((1200, 600))
        self.background_image = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor="nw", image=self.background_image, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI, tags="overlay")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI2, tags="overlay")

        # Information text
        file_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/Announcements/Announcement%20Window.txt"
        text_content = self.fetch_text_from_github(file_url)
        text_contentoutline = self.fetch_text_from_github(file_url)
        text_widgetoutline2 = canvas.create_text(1001, 126, text=text_content, fill="black", font=("Arial Bold", 14, "bold"), anchor="center", justify="center", width=325)
        text_widget = canvas.create_text(1000, 125, text=text_content, fill="#FBF8F3", font=("Arial Bold", 14, "bold"), anchor="center", justify="center", width=325)

        # Create preset menu.
        presets_data = self.fetch_presets_from_github()
        if presets_data is None:
            self.presets = self.get_local_presets()
        else:
            self.presets = presets_data
        self.presets = {"Saved": {}} | self.presets
        self.preset_label = canvas.create_text(40, 40, text="Select Preset:", anchor="w", fill="#D1F3FD", font=textfont)
        self.selected_preset = tk.StringVar(value="Saved")
        self.preset_dropdown = ttk.Combobox(window, textvariable=self.selected_preset, values=list(self.presets.keys()))
        self.preset_dropdown_window = canvas.create_window(200, 40, anchor="w", window=self.preset_dropdown)
        self.preset_dropdown.bind("<<ComboboxSelected>>", self.apply_selected_preset)
        # Setting Preset
        self.Settings_label = canvas.create_text(350, 40, text="Yuzu Settings:", anchor="w", fill="#D1F3FD", font=textfont)
        self.selected_settings = tk.StringVar(value="No Change")
        self.second_dropdown = ttk.Combobox(window, textvariable=self.selected_settings, values=["No Change", "Steamdeck", "AMD", "Nvidia", "High End Nvidia"])
        self.second_dropdown_window = canvas.create_window(450, 40, anchor="w", window=self.second_dropdown)
        self.second_dropdown.bind("<<ComboboxSelected>>")

        # Create a label for yuzu.exe selection
        canvas.create_text(40, 80, text="Select yuzu.exe:", anchor="w", fill="#D1F3FD", font=textfont)
        backupbutton = 200
        if self.os_platform == "Windows":
            yuzu_button = ttk.Button(window, text="Browse", command=self.select_yuzu_exe)
            yuzu_button_window = canvas.create_window(200, 80, anchor="w", window=yuzu_button)
            # Reset to Appdata
            reset_button = ttk.Button(window, text="Use Appdata", command=self.yuzu_appdata)
            reset_button_window = canvas.create_window(300, 80, anchor="w", window=reset_button)
            backupbutton = 400


        # Create a Backup button
        backup_button = ttk.Button(window, text="Backup", command=self.backup)
        backup_button_window = canvas.create_window(backupbutton, 80, anchor="w", window=backup_button)

        # Create a label for resolution selection
        canvas.create_text(40, 120, text="Select a Resolution:", anchor="w", fill="#D1F3FD", font=textfont)
        self.resolution_var = tk.StringVar(value=self.dfps_options.get("ResolutionNames", [""])[2])  # Set the default resolution to "1080p FHD"
        resolution_dropdown = ttk.Combobox(window, textvariable=self.resolution_var, values=self.dfps_options.get("ResolutionNames", []))
        resolution_dropdown_window = canvas.create_window(200, 120, anchor="w", window=resolution_dropdown)
        resolution_dropdown.bind("<<ComboboxSelected>>", lambda event: self.warning_window("Res"))

        # Create a label for FPS selection
        canvas.create_text(40, 160, text="Select an FPS:", anchor="w", fill="#D1F3FD", font=textfont)
        self.fps_var = tk.StringVar(value=str(self.dfps_options.get("FPS", [])[2]))  # Set the default FPS to 60
        fps_dropdown = ttk.Combobox(window, textvariable=self.fps_var, values=self.dfps_options.get("FPS", []))
        fps_dropdown_window = canvas.create_window(200, 160, anchor="w", window=fps_dropdown)

        # Create a label for shadow resolution selection
        canvas.create_text(40, 200, text="Shadow Resolution:", anchor="w", fill="#D1F3FD", font=textfont)
        self.shadow_resolution_var = tk.StringVar(value=self.dfps_options.get("ShadowResolutionNames", [""])[0])  # Set the default shadow resolution to "Auto"
        shadow_resolution_dropdown = ttk.Combobox(window, textvariable=self.shadow_resolution_var, values=self.dfps_options.get("ShadowResolutionNames", []))
        shadow_resolution_dropdown_window = canvas.create_window(200, 200, anchor="w", window=shadow_resolution_dropdown)

        # Create a Label for camera quality
        canvas.create_text(40, 240, text="Camera Quality:", anchor="w", fill="#D1F3FD", font=textfont)
        self.camera_var = tk.StringVar(value=self.dfps_options.get("CameraQualityNames", [""])[0])  # Set the default camera quality to "Enable"
        camera_dropdown = ttk.Combobox(window, textvariable=self.camera_var, values=self.dfps_options.get("CameraQualityNames", []))
        camera_dropdown_window = canvas.create_window(200, 240, anchor="w", window=camera_dropdown)

        # Create a label for UI selection
        canvas.create_text(40, 280, text="Select a UI:", anchor="w", fill="#D1F3FD", font=textfont)
        ui_values = ["None", "Black Screen Fix", "PS4", "Xbox"]
        self.ui_var = tk.StringVar(value=ui_values[0])
        ui_dropdown = ttk.Combobox(window, textvariable=self.ui_var, values=ui_values)
        ui_dropdown_window = canvas.create_window(200, 280, anchor="w", window=ui_dropdown)

        # First Person and FOV
        canvas.create_text(40, 320, text="Enable First Person:", anchor="w", fill="#D1F3FD", font=textfont)
        fp_values = ["Disabled", "70 FOV", "90 FOV", "110 FOV"]
        self.fp_var = tk.StringVar(value=ui_values[0])
        fp_dropdown = ttk.Combobox(window, textvariable=self.fp_var, values=fp_values)
        fp_dropdown_window = canvas.create_window(200, 320, anchor="w", window=fp_dropdown)

        # Create labels and enable/disable options for each entry
        self.selected_options = {}
        row = 320
        for version_option_name, version_option_value in self.version_options[0].items():
            # Exclude specific keys from being displayed
            if version_option_name in ["Source", "nsobid", "offset", "version"]:
                continue

            # Create label
            if version_option_name not in ["Source", "nsobid", "offset", "version"]:
                canvas.create_text(40, row + 40, text=version_option_name, anchor="w", fill="#D1F3FD", font=textfont)

            # Create enable/disable dropdown menu
            version_option_var = tk.StringVar(value="Enable")
            version_option_dropdown = ttk.Combobox(window, textvariable=version_option_var, values=["Enable", "Disable"])
            version_option_dropdown_window = canvas.create_window(200, row + 40, anchor="w", window=version_option_dropdown)

            self.selected_options[version_option_name] = version_option_var
            row += 40

        # Ko-fi Button
        kofi_image_path = self.get_UI_path("Kofi.png")
        kofi_image = Image.open(kofi_image_path)
        kofi_image = kofi_image.resize((150, 42))
        self.kofi_image = ImageTk.PhotoImage(kofi_image)
        kofi_button = ttk.Button(window, image=self.kofi_image, command=self.open_kofi)
        kofi_button_window = canvas.create_window(1110, 550, anchor="center", window=kofi_button)

        # GitHub Button
        github_image_path = self.get_UI_path("github.png")
        github_image = Image.open(github_image_path)
        github_image = github_image.resize((76, 40))
        self.github_image = ImageTk.PhotoImage(github_image)
        github_button = ttk.Button(window, image=self.github_image, command=self.open_github)
        github_button_window = canvas.create_window(980, 550, anchor="center", window=github_button)

        # Create a submit button
        submit_button = ttk.Button(window, text="Save", command=self.submit)
        submit_button_window = canvas.create_window(200, row + 40, anchor="w", window=submit_button)

        # Load Saved User Options.
        config_file = "VisualImprovements.ini"
        self.load_user_choices(config_file)
    # run UI properly as executable
    def get_UI_path(self, file_name):
        if getattr(sys, 'frozen', False):
            # Look for the 'HUD' folder next to the executable
            executable_dir = os.path.dirname(sys.executable)
            hud_folder_path = os.path.join(executable_dir, "HUD")
            if os.path.exists(hud_folder_path):
                return os.path.abspath(os.path.join(hud_folder_path, file_name))
        # If not running as an executable or 'HUD' folder not found, assume it's in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        hud_folder_path = os.path.join(script_dir, "HUD")
        return os.path.abspath(os.path.join(hud_folder_path, file_name))
    # Define OS
    def DetectOS(self):
        if self.os_platform == "Linux":
            print("Detected a Linux based SYSTEM!")
        elif self.os_platform == "Windows":
            print("Detected a Windows based SYSTEM!")
    # Define Directories for different OS or Yuzu Folders, Check if User has correct paths for User Folder.
    def checkpath(self):
        home_directory = os.path.expanduser("~")
        # Default Dir for Linux/SteamOS
        self.os_platform = platform.system()
        if self.os_platform == "Linux":
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
        # Default Dir for Windows or user folder.
        elif self.os_platform == "Windows":
            config = "VisualImprovements.ini"
            yuzupath = self.load_yuzu_path(config)
            userfolder = os.path.join(yuzupath, "../user/")
            # Check for user folder
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
    # Handle Presets
    def apply_selected_preset(self, event=None):
        selected_preset = self.selected_preset.get()

        if selected_preset == "None":
            config_file = "VisualImprovements.ini"
            if os.path.exists(config_file):
                self.load_user_choices(config_file)
            else:
                # Fallback to the default preset
                default_preset = self.get_local_presets().get("Default", {})
                self.apply_preset(default_preset)
        
        elif selected_preset == "Saved":
            config_file = "VisualImprovements.ini"
            if os.path.exists(config_file):
                self.load_user_choices(config_file)
            else:
                messagebox.showinfo("Saved Preset", "No saved preset found. Please save your current settings first.")
        elif selected_preset in self.presets_data:
            # Apply the selected preset from the online presets
            self.apply_preset(self.presets[selected_preset])
    #fetch presets
    def fetch_presets_from_github(self):
        presets_folder = "json.data"
        if not os.path.exists(presets_folder):
            os.makedirs(presets_folder)
        github_raw_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/presets.json"
        presets_file_path = os.path.join(presets_folder, "presets.json")

        try:
            response = requests.get(github_raw_url)
            if response.status_code == 200:
                github_presets_data = response.json()

                if os.path.exists(presets_file_path):
                    with open(presets_file_path, "r") as file:
                        local_presets_data = json.load(file)

                    if github_presets_data != local_presets_data:
                        with open(presets_file_path, "w") as file:
                            json.dump(github_presets_data, file)
                            self.presets_data = github_presets_data
                    else:
                        self.presets_data = local_presets_data
                else:
                    with open(presets_file_path, "w") as file:
                        json.dump(github_presets_data, file)
                        self.presets_data = github_presets_data
            else:
                if os.path.exists(presets_file_path):
                    with open(presets_file_path, "r") as file:
                        self.presets_data = json.load(file)
                else:
                    self.presets_data = {}

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            # If fetching or parsing fails, use the local file if available
            print(f"Error occurred while fetching or parsing presets.json from GitHub: {e}")
            if os.path.exists(presets_file_path):
                with open(presets_file_path, "r") as file:
                    self.presets_data = json.load(file)
            else:
                # If both GitHub and local presets are not available, set to empty dictionary
                self.presets_data = {}

        return self.presets_data

    def load_dfps_options_from_json(self):
        # Check if the .presets folder exists, if not, create it
        presets_folder = "json.data"
        if not os.path.exists(presets_folder):
            os.makedirs(presets_folder)
        json_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/DFPS.json"
        dfps_options_file_path = os.path.join(presets_folder, "DFPS.json")

        try:
            response = requests.get(json_url)
            data = response.json()

            if os.path.exists(dfps_options_file_path):
                with open(dfps_options_file_path, "r") as file:
                    local_dfps_options = json.load(file)

                if data != local_dfps_options:
                    with open(dfps_options_file_path, "w") as file:
                        json.dump(data, file)
                        self.dfps_options = data
                else:
                    self.dfps_options = local_dfps_options
            else:
                with open(dfps_options_file_path, "w") as file:
                    json.dump(data, file)
                    self.dfps_options = data
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error occurred while fetching or parsing DFPS.json: {e}")
            if os.path.exists(dfps_options_file_path):
                with open(dfps_options_file_path, "r") as file:
                    self.dfps_options = json.load(file)
            else:
                self.dfps_options = {}

        return self.dfps_options

    def load_version_options_from_json(self):
        # Check if the .presets folder exists, if not, create it
        presets_folder = "json.data"
        if not os.path.exists(presets_folder):
            os.makedirs(presets_folder)
        json_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/settings/Version.json"
        version_options_file_path = os.path.join(presets_folder, "Version.json")

        try:
            response = requests.get(json_url, timeout=5)
            response.raise_for_status()

            data = response.json()

            if os.path.exists(version_options_file_path):
                with open(version_options_file_path, "r") as file:
                    local_version_options = json.load(file)

                if data != local_version_options:
                    with open(version_options_file_path, "w") as file:
                        json.dump(data, file)
                        self.version_options = data
                else:
                    self.version_options = local_version_options
            else:
                with open(version_options_file_path, "w") as file:
                    json.dump(data, file)
                    self.version_options = data

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Error occurred while fetching or parsing Version.json: {e}")
            if os.path.exists(version_options_file_path):
                with open(version_options_file_path, "r") as file:
                    self.version_options = json.load(file)
            else:
                self.version_options = []

        return self.version_options
    # Apply Presets
    def apply_preset(self, preset_options):
        self.resolution_var.set(preset_options.get("Resolution", ""))
        self.fps_var.set(preset_options.get("FPS", ""))
        self.shadow_resolution_var.set(preset_options.get("ShadowResolution", ""))
        self.camera_var.set(preset_options.get("CameraQuality", ""))
        self.ui_var.set(preset_options.get("UI", ""))
        self.fp_var.set(preset_options.get("First Person", ""))

        skip_keys = ["Resolution", "FPS", "ShadowResolution", "CameraQuality", "UI"]

        for option_key, option_value in preset_options.items():
            # Check if the option exists in the self.selected_options dictionary and not in the skip_keys
            if option_key in self.selected_options and option_key not in skip_keys:
                self.selected_options[option_key].set(option_value)
            else:
                continue
    # Select Yuzu Dir
    def select_yuzu_exe(self):
        # Open a file dialog to browse and select yuzu.exe
        if self.os_platform == "Windows":
            yuzu_path = filedialog.askopenfilename(
                filetypes=[("Executable files", "*.exe"), ("All Files", "*.*")]
            )
            home_directory = os.path.dirname(self.yuzu_path)
            Default_Directory = os.path.join(home_directory, "user")

            if yuzu_path:
                # Save the selected yuzu.exe path to a configuration file
                config_file = "VisualImprovements.ini"
                self.save_user_choices(config_file, yuzu_path)
                home_directory = os.path.dirname(yuzu_path)
                if os.path.exists(Default_Directory):
                    self.Yuzudir = os.path.join(home_directory, "user", "load", "0100F2C0115B6000")
                    print(f"Successfully selected Yuzu.exe! And a user folder was found at {home_directory}!")
                    self.checkpath()
                else:
                    print("User Folder not Found defaulting to Yuzu Dir!")
                    self.checkpath()

                # Update the yuzu.exe path in the current session
                self.yuzu_path = yuzu_path
            else:
                self.checkpath()
            # Save the selected yuzu.exe path to a configuration file
            config_file = "VisualImprovements.ini"
            self.save_user_choices(config_file, yuzu_path)
        else: print(f"You are not running Windows this feature is disabled, defaulting to {self.Yuzudir}")
        return
    # Return Yuzu Dir to Appdata (Windows ONLY)
    def yuzu_appdata(self):
        self.checkpath()
        print("Successfully Defaulted to Appdata!")
        config_file = "VisualImprovements.ini"
        self.save_user_choices(config_file, "appdata")
    # Load Yuzu Dir
    def load_yuzu_path(self, config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            yuzu_path = config.get('Paths', 'YuzuPath', fallback="Appdata")
            return yuzu_path
    # Download Manager
    @staticmethod
    def download_file(url, save_path):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded file: {save_path}")
        else:
            print(f"Failed to download file from {url}. Status code: {response.status_code}")

    def copy_files_and_subfolders(contents, Mod_directory):
         for item in contents:
             if item['type'] == 'file':
                file_url = item.get('download_url')
                file_name = os.path.join(Mod_directory, item['name'])

                file_response = requests.get(file_url)
                if file_response.status_code == 200:
                   with open(file_name, 'wb') as file:
                       file.write(file_response.content)
                   print(f'copied file: {file_name}')
             elif item['type'] == "dir":
                 folder_name = os.path.join(Mod_directory, item['name'])
                 os.makedirs(folder_name, exist_ok=True)
                 subfolder_contents = Manager.get_folder_contents(item['url'])
                 Manager.copy_files_and_subfolders(subfolder_contents, folder_name)

    def get_folder_contents(api_url):
        response = requests.get(api_url)
        if response.status_code == 200:
           return response.json()

    def save_user_choices(self, config_file, yuzu_path=None):
        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file)

        # Save the selected options
        config['Options'] = {}
        config['Options']['Resolution'] = self.resolution_var.get()
        config['Options']['FPS'] = self.fps_var.get()
        config['Options']['ShadowResolution'] = self.shadow_resolution_var.get()
        config['Options']['CameraQuality'] = self.camera_var.get()
        config['Options']['UI'] = self.ui_var.get()
        config['Options']['First Person'] = self.fp_var.get()

        # Save the enable/disable choices
        for option_name, option_var in self.selected_options.items():
            config['Options'][option_name] = option_var.get()

        # Save the yuzu.exe path if provided
        if yuzu_path:
            config['Paths'] = {'YuzuPath': yuzu_path}

        # Write the updated configuration back to the file
        with open(config_file, 'w') as file:
            config.write(file)

    def load_user_choices(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        # Load the selected options
        self.resolution_var.set(config.get('Options', 'Resolution', fallback=self.dfps_options.get("ResolutionNames", [""])[2]))
        self.fps_var.set(config.get('Options', 'FPS', fallback=str(self.dfps_options.get("FPS", [])[2])))
        self.shadow_resolution_var.set(config.get('Options', 'ShadowResolution', fallback=self.dfps_options.get("ShadowResolutionNames", [""])[0])) # Shadow Auto
        self.camera_var.set(config.get('Options', 'CameraQuality', fallback=self.dfps_options.get("CameraQualityNames", [""])[0]))
        ui_selection = config.get('Options', 'UI', fallback="None")
        fp_selection = config.get('Options', 'First Person', fallback="Disabled")
        # Neccessary to FIX ui, won't download otherwise.
        if fp_selection in ["Disabled", "70 FOV", "90 FOV", "110 FOV"]:
           self.fp_var.set(fp_selection)
        else:
           self.fp_var.set("Disabled")
        # Neccessary to FIX ui, won't download otherwise.
        if ui_selection in ["None", "Black Screen Fix", "PS4", "Xbox"]:
           self.ui_var.set(ui_selection)
        else:
           self.ui_var.set("None")
        # Load the enable/disable choices
        for option_name, option_var in self.selected_options.items():
            option_value = config.get('Options', option_name, fallback="Enable")
            option_var.set(option_value)

        self.yuzu_path = self.load_yuzu_path(config_file)

        if self.yuzu_path:
            home_directory = os.path.dirname(self.yuzu_path)
            Default_Directory = os.path.join(home_directory, "user")

            if os.path.exists(Default_Directory):
                self.Yuzudir = os.path.join(home_directory, "user", "load", "0100F2C0115B6000")
                print(f"User Folder Found! New mod path! {self.Yuzudir}")
            
            else:
                print("User Folder not Found defaulting to Default Dir!")
                self.checkpath()
        else:
            print("Yuzu path not found in the config file - Defaulting to Default Dir!")
            self.checkpath()
 
    def warning_window(self, setting_type):
        warning_message = None
        configfile = self.TOTKconfig
        print(f"{configfile}")
        config = configparser.ConfigParser()
        config.read(configfile)

        if setting_type == "Res":
            resolution = self.resolution_var.get()
            Resindex = self.dfps_options.get("ResolutionNames").index(resolution)
            current_res = self.dfps_options.get("ResolutionValues", [""])[Resindex].split("x")[1]
            proper_res = float(current_res)
            if not config.has_section("Core"):
                config.add_section("Core")
            try:
                mem1 = config.get("Core", "use_unsafe_extended_memory_layout\\use_global")
                mem2 = config.get("Core", "use_unsafe_extended_memory_layout\\default")
                mem3 = config.get("Core", "use_unsafe_extended_memory_layout") # true = 8gb - doesn't work anymore in new version of Yuzu
                newmem1 = config.get("Core", "memory_layout_mode\\use_global")
                newmem2 = config.get("Core", "memory_layout_mode\\default")
                newmemsetting = int(config.get("Core", "memory_layout_mode")) # 0 - 4gb, 1 - 6gb, 2 - 8gb
                res1 = config.get("Renderer", "resolution_setup\\use_global")
                res2 = config.get("Renderer", "resolution_setup\\default")
                res3 = int(config.get("Renderer", "resolution_setup"))
            except configparser.NoOptionError as e:
                mem1 = "true"
                mem2 = "true"
                mem3 = "false"
                newmem1 = "true"
                newmem2 = "true"
                newmemsetting = 0
                res1 = "true"
                res1 = "true"
                res3 = 0

            if proper_res > 1080:
                if mem3 == "false" or newmemsetting == 0 or not res3 == 2 or not newmem1 == "false" or not newmem2 == "false" or not mem1 == "false" or not mem2 == "false":
                    file_path = self.TOTKconfig
                    warning_message = f"Resolution {resolution}, requires 1x Yuzu renderer and extended memory layout 8GB to be enabled, otherwise it won't function properly and will cause artifacts, you currently have them disabled, do you want to enable them?"
                else:
                    print("Correct settings are already applied, no changes required!!")
            else:
                print("Resolution is lower than 1080p! No changes required!")

        if warning_message is not None and warning_message.strip():
            response = messagebox.askyesno(f"WARNING! Required settings NOT Enabled!", warning_message)
            # If Yes, Modify the Config File.
            if response:
                # Remove existing options in Renderer section
                if config.has_section("Renderer"):
                    if config.has_option("Renderer", "resolution_setup\\use_global"):
                        config.remove_option("Renderer", "resolution_setup\\use_global")
                    if config.has_option("Renderer", "resolution_setup\\default"):
                        config.remove_option("Renderer", "resolution_setup\\default")
                    if config.has_option("Renderer", "resolution_setup"):
                        config.remove_option("Renderer", "resolution_setup")

                # Remove existing options in Core section
                if config.has_section("Core"):
                    if config.has_option("Core", "use_unsafe_extended_memory_layout\\use_global"):
                        config.remove_option("Core", "use_unsafe_extended_memory_layout\\use_global")
                    if config.has_option("Core", "use_unsafe_extended_memory_layout\\default"):
                        config.remove_option("Core", "use_unsafe_extended_memory_layout\\default")
                    if config.has_option("Core", "use_unsafe_extended_memory_layout"):
                        config.remove_option("Core", "use_unsafe_extended_memory_layout")
                    if config.has_option("Core", "memory_layout_mode\\use_global"):
                        config.remove_option("Core", "memory_layout_mode\\use_global")
                    if config.has_option("Core", "memory_layout_mode\\default"):
                        config.remove_option("Core", "memory_layout_mode\\default")
                    if config.has_option("Core", "memory_layout_mode"):
                        config.remove_option("Core", "memory_layout_mode")
                # Add new values
                config.set("Renderer", "resolution_setup\\use_global", "false")
                config.set("Renderer", "resolution_setup\\default", "false")
                config.set("Renderer", "resolution_setup", "2")

                config.set("Core", "use_unsafe_extended_memory_layout\\use_global", "false")
                config.set("Core", "use_unsafe_extended_memory_layout\\default", "false")
                config.set("Core", "use_unsafe_extended_memory_layout", "true")
                config.set("Core", "memory_layout_mode\\use_global", "false")
                config.set("Core", "memory_layout_mode\\default", "false")
                config.set("Core", "memory_layout_mode", "1")

                with open(configfile, "w") as configfile:
                    config.write(configfile, space_around_delimiters=False)
            else:
                # If No, do nothing.
                print(f"Turning on required settings declined!!")
    # Open Kofi
    def open_kofi(self):
        import webbrowser
        webbrowser.open("https://ko-fi.com/maxlastbreath#")
    # Open Github
    def open_github(self):
        import webbrowser
        webbrowser.open("https://github.com/MaxLastBreath/TOTK-mods")
    # Handle Text Window
    def fetch_text_from_github(self, file_url):
        try:
            response = requests.get(file_url)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error: Unable to fetch text from Github")
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while fetching text: {e}")

        return ""
    # Handle Save Backups
    def backup(self):
        # Fetch the nand_directory value from the qt-config.ini file
        testforuserdir = os.path.join(self.nand_dir, "user", "save", "0000000000000000")
        testforuser = os.listdir(testforuserdir)
        target_folder = "0100F2C0115B6000"
        # checks each individual folder ID for each user and finds the ones with saves for TOTK. Then backups the TOTK saves!
        for root, dirs, files in os.walk(testforuserdir):
            if target_folder in dirs:
                folder_to_backup = os.path.join(root, target_folder)
        print(f"Attemping to backup {folder_to_backup}")
        # Create the 'backup' folder inside the mod manager directory if it doesn't exist
        script_dir = os.path.dirname(os.path.abspath(sys.executable))
        backup_folder_path = os.path.join(script_dir, "backup")
        os.makedirs(backup_folder_path, exist_ok=True)
        backup_file = "Save.rar"
        file_number = 1
        while os.path.exists(os.path.join(backup_folder_path, backup_file)):
            backup_file = f"Save_{file_number}.rar"
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
            messagebox.showerror("Backup Error", f"Error creating backup: {e}")
    # Submit the results, run download manager. Open a Loading screen.
    def submit(self):
        self.checkpath()
        def timer(value):
            progress_bar["value"] = value
            self.window.update_idletasks()
        def run_tasks():
            timer(20)
            DownloadFP()
            timer(40)
            DownloadUI()
            timer(50)
            DownloadDFPS()
            timer(80)
            UpdateVisualImprovements()
            timer(100)
            UpdateSettings()
            progress_window.destroy()
        def UpdateVisualImprovements():
            config_file = "VisualImprovements.ini"
            self.save_user_choices(config_file)

            resolution = self.resolution_var.get()
            fps = self.fps_var.get()
            shadow_resolution = self.shadow_resolution_var.get()
            camera_quality = self.camera_var.get()

            # Determine the path to the INI file in the user's home directory
            ini_file_directory = os.path.join(self.load_dir, "Mod Manager Patch", "romfs", "dfps")
            os.makedirs(ini_file_directory, exist_ok=True)
            ini_file_path = os.path.join(ini_file_directory, "default.ini")

            # Remove the previous default.ini file if it exists - DFPS settings.
            if os.path.exists(ini_file_path):
                os.remove(ini_file_path)

            # Save the selected options to the INI file
            config = configparser.ConfigParser() 
            config.optionxform = lambda option: option

            # Add the selected resolution, FPS, shadow resolution, and camera quality
            self.Resindex = self.dfps_options.get("ResolutionNames").index(resolution)
            ShadowIndex = self.dfps_options.get("ShadowResolutionNames").index(shadow_resolution)
            CameraIndex = self.dfps_options.get("CameraQualityNames").index(camera_quality)

            config['Graphics'] = {
                'ResolutionWidth': self.dfps_options.get("ResolutionValues", [""])[self.Resindex].split("x")[0],
                'ResolutionHeight': self.dfps_options.get("ResolutionValues", [""])[self.Resindex].split("x")[1],
                'ResolutionShadows': self.dfps_options.get("ShadowResolutionValues", [""])[ShadowIndex]
            }
            config['dFPS'] = {'MaxFramerate': fps}
            config['Features'] = {'EnableCameraQualityImprovement': self.dfps_options.get("CameraQualityValues", [""])[CameraIndex]}

            selected_options = {}

            for option_name, option_var in self.selected_options.items():
                selected_options[option_name] = option_var.get()

            # Logic for Updating Visual Improvements Mod
            for version_option in self.version_options:
                version = version_option.get("version", "")
                mod_path = os.path.join(self.load_dir, "Mod Manager Patch", "exefs")

                # Create the directory if it doesn't exist
                os.makedirs(mod_path, exist_ok=True)

                filename = os.path.join(mod_path, f"{version}.pchtxt")
                with open(filename, "w") as file:
                    file.write(version_option.get("Source", "") + "\n")
                    file.write(version_option.get("nsobid", "") + "\n")
                    file.write(version_option.get("offset", "") + "\n")

                    for key, value in version_option.items():
                        if key not in ["Source", "nsobid", "offset", "version"] and key in selected_options and selected_options[key] == "Enable":
                            file.write(value + "\n")
    
            # Update Visual Improvements MOD.
            with open(ini_file_path, 'w') as configfile:
                config.write(configfile)
        def UpdateSettings():
            Setting_folder = None
            SettingGithubFolder = None
            Setting_selection = self.selected_settings.get()
            print(f"{Setting_selection}")
            print(f"{self.load_dir}")
            if Setting_selection == "No Change":
                print("No Yuzu Settings have been changed!")
                return
            elif Setting_selection == "Steamdeck":
                     Setting_folder = "Steamdeck"
                     SettingGithubFolder = "scripts/settings/Applied%20Settings/Steamdeck/0100F2C0115B6000.ini"
                     print("Installing steamdeck Yuzu preset")
            elif Setting_selection == "AMD":
                     Setting_folder = "AMD"
                     SettingGithubFolder = 'scripts/settings/Applied%20Settings/AMD/0100F2C0115B6000.ini'
                     print("Installing AMD Yuzu Preset")
            elif Setting_selection == "Nvidia":
                     Setting_folder = "Nvidia"
                     SettingGithubFolder = 'scripts/settings/Applied%20Settings/Nvidia/0100F2C0115B6000.ini'
                     print("Installing Nvidia Yuzu Preset")
            elif Setting_selection == "High End Nvidia":
                     Setting_folder = "High End Nvidia"
                     SettingGithubFolder = 'scripts/settings/Applied%20Settings/High%20End%20Nvidia/0100F2C0115B6000.ini'
                     print("Installing High End Nvidia Yuzu Preset")
            if Setting_selection is not None:
                    repo_url = 'https://github.com/MaxLastBreath/TOTK-mods'
                    Setting_directory = self.TOTKconfig
                    raw_url = f'{repo_url}/raw/main/{SettingGithubFolder}'
                    response = requests.get(raw_url)
                    if response.status_code == 200:
                        with open(Setting_directory, "wb") as file:
                            file.write(response.content)
                        print("Successfully Installed TOTK Yuzu preset settings!")
                        current_res = self.dfps_options.get("ResolutionValues", [""])[self.Resindex].split("x")[1]
                        proper_res = float(current_res)
                    else:
                        print(f"Failed to download file from {raw_url}. Status code: {response.status_code}")
                        return
                    if proper_res > 1080:
                        configfile = self.TOTKconfig
                        print(f"{configfile}")
                        config = configparser.ConfigParser()
                        config.read(configfile)
                        if config.has_option("Renderer", "resolution_setup\\use_global"):
                            config.remove_option("Renderer", "resolution_setup\\use_global")
                        if config.has_option("Renderer", "resolution_setup\\default"):
                            config.remove_option("Renderer", "resolution_setup\\default")
                        if config.has_option("Renderer", "resolution_setup"):
                            config.remove_option("Renderer", "resolution_setup")

                        # Remove existing options in Core section
                        if config.has_option("Core", "use_unsafe_extended_memory_layout\\use_global"):
                            config.remove_option("Core", "use_unsafe_extended_memory_layout\\use_global")
                        if config.has_option("Core", "use_unsafe_extended_memory_layout\\default"):
                            config.remove_option("Core", "use_unsafe_extended_memory_layout\\default")
                        if config.has_option("Core", "use_unsafe_extended_memory_layout"):
                            config.remove_option("Core", "use_unsafe_extended_memory_layout")
                        if config.has_option("Core", "memory_layout_mode\\use_global"):
                            config.remove_option("Core", "memory_layout_mode\\use_global")
                        if config.has_option("Core", "memory_layout_mode\\default"):
                            config.remove_option("Core", "memory_layout_mode\\default")
                        if config.has_option("Core", "memory_layout_mode"):
                            config.remove_option("Core", "memory_layout_mode")
                        # Add new values
                        config.set("Renderer", "resolution_setup\\use_global", "false")
                        config.set("Renderer", "resolution_setup\\default","false")
                        config.set("Renderer", "resolution_setup", "2")

                        config.set("Core", "use_unsafe_extended_memory_layout\\use_global", "false")
                        config.set("Core", "use_unsafe_extended_memory_layout\\default", "false")
                        config.set("Core", "use_unsafe_extended_memory_layout", "true")
                        config.set("Core", "memory_layout_mode\\use_global", "false")
                        config.set("Core", "memory_layout_mode\\default", "false")
                        config.set("Core", "memory_layout_mode", "1")
                        with open(configfile, "w") as configfile:
                            config.write(configfile)
            else:
                print("Selected option has no associated setting folder.")
        def DownloadDFPS():
            config = configparser.ConfigParser()
            config_file = "VisualImprovements.ini"
            config.read(config_file)
            if not config.has_section("Updates"):
                config.add_section("Updates")
                config.set("Updates", "dfps", "1.0.0")
                with open(config_file, "w") as configfile:
                    config.write(configfile)
            try:
                latest_dfps_version = config.get("Updates", "dfps")
            except NoOptionError as e:
                # Handle the case when "dfps" option doesn't exist
                config.set("Updates", "dfps", "1.0.0")
                with open(config_file, "w") as configfile:
                    config.write(configfile)
                latest_dfps_version = "1.0.0"
            print(f"Successfully updated config!")

            current_dfps_version = self.dfps_options.get("DFPS Version")
            # Start of DFPS file check.
            if current_dfps_version != latest_dfps_version or not os.path.exists(os.path.join(self.load_dir, "DFPS", "exefs")):
                dfps_directory = os.path.join(self.load_dir, "DFPS", "exefs")
                os.makedirs(dfps_directory, exist_ok=True)
                file_urls = [
                    {
                        "url": "https://github.com/MaxLastBreath/TOTK-mods/raw/main/scripts/DFPS/main.npdm",
                        "save_path": os.path.join(dfps_directory, "main.npdm")
                    },
                    {
                        "url": "https://github.com/MaxLastBreath/TOTK-mods/raw/main/scripts/DFPS/subsdk9",
                        "save_path": os.path.join(dfps_directory, "subsdk9")
                    }
                ]
                for file_info in file_urls:
                    url = file_info["url"]
                    save_path = file_info["save_path"]

                    print("Checking for updates")
                    Manager.download_file(url, save_path)
                # Update Config File
                config.set("Updates", "dfps", current_dfps_version)
                with open(config_file, "w") as configfile:
                    config.write(configfile)
            else:
                print("You already have the latest DFPS version and the folder exists!")
        def DownloadUI():
            ui_mod_folder = None
            CurrentFolder = None
            ui_selection = self.ui_var.get()
            print(f"{self.fp_var.get()}")
            if ui_selection == "none":
               print("No UI Selected")
            elif ui_selection == "PS4":
                     ui_mod_folder = "Playstation UI"
                     CurrentFolder = "scripts/UI/Playstation%20UI/"
            elif ui_selection == "Xbox":
                     ui_mod_folder = "Xbox UI"
                     CurrentFolder = 'scripts/UI/Xbox%20UI/'
            elif ui_selection == "Black Screen Fix":
                     ui_mod_folder = "BlackscreenFix"
                     CurrentFolder = 'scripts/UI/BlackscreenFix/'

            if ui_mod_folder is not None:
                    repo_url = 'https://api.github.com/repos/MaxLastBreath/TOTK-mods'
                    folder_path = f'{CurrentFolder}'
                    Mod_directory = os.path.join(self.load_dir, f'{ui_mod_folder}')

                    if os.path.exists(Mod_directory):
                        print(f"The UI mod folder '{ui_mod_folder}' already exists. Skipping download.")
                        return
                    api_url = f'{repo_url}/contents/{folder_path}'
                    response = requests.get(api_url)
            
                    if response.status_code == 200:
                        contents = response.json()
                        os.makedirs(Mod_directory, exist_ok=True)
                        Manager.copy_files_and_subfolders(contents, Mod_directory)
                        return
                    else:
                        print("failed to retrive folder and contents")
        def DownloadFP():
            FP_mod_folder = None
            FPCurrentFolder = None
            FP_selection = self.fp_var.get()
            if FP_selection == "Disabled":
                print("Third Person is selected!")
            elif FP_selection == "70 FOV":
                     FP_mod_folder = "First Person 70 FOV"
                     FPCurrentFolder = "scripts/UI/First%20Person%20FOV%2070/"
            elif FP_selection == "90 FOV":
                     FP_mod_folder = "First Person 90 FOV"
                     FPCurrentFolder = 'scripts/UI/First%20Person%20FOV%2090/'
            elif FP_selection == "110 FOV":
                     FP_mod_folder = "First Person 110 FOV"
                     FPCurrentFolder = 'scripts/UI/First%20Person%20FOV%20110/'
            if FP_mod_folder is not None:
                    repo_url = 'https://api.github.com/repos/MaxLastBreath/TOTK-mods'
                    FPfolder_path = f'{FPCurrentFolder}'
                    FPMod_directory = os.path.join(self.load_dir, f'{FP_mod_folder}')

                    if os.path.exists(FPMod_directory):
                        print(f"The FP mod folder '{FP_mod_folder}' already exists. Skipping download.")
                        return
                 
                    api_url = f'{repo_url}/contents/{FPfolder_path}'
                    response = requests.get(api_url)
            
                    if response.status_code == 200:
                        contents = response.json()
                        os.makedirs(FPMod_directory, exist_ok=True)
                        Manager.copy_files_and_subfolders(contents, FPMod_directory)
                        return
                    else:
                        print("failed to retrive folder and contents")
        # Execute tasks and make a Progress Window.
        progress_window = Toplevel(self.root)
        progress_window.title("Downloading")
        window_width = 300
        window_height = 100
        screen_width = progress_window.winfo_screenwidth()
        screen_height = progress_window.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        progress_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        total_iterations = 100
        progress_bar = ttk.Progressbar(progress_window, mode="determinate", maximum=total_iterations)
        progress_bar.pack(pady=20)
        task_thread = threading.Thread(target=run_tasks)
        task_thread.start()