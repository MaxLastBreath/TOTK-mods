import tkinter as tk
from tkinter import Event, ttk, filedialog, messagebox, Toplevel
import configparser
import threading
import os
import sys
import shutil
import json
import requests
import ttkbootstrap as ttk
import time
import webbrowser
import re
from idlelib.tooltip import Hovertip
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, ImageFilter, ImageOps
from configparser import NoOptionError
from modules.qt_config import modify_disabled_key, get_config_parser
from modules.checkpath import checkpath, DetectOS
from modules.json import load_json
from modules.backup import backup
from modules.config import save_user_choices, load_user_choices
from configuration.settings import Hoverdelay, title_id, localconfig, textfont, style, sf, textcolor, outlinecolor, dfpsurl, cheatsurl, versionurl, presetsurl, descurl, bigfont, BigTextcolor


class Manager:
    
    def __init__(self, window):
        # Set Variables
        self.config = localconfig
        config = configparser.ConfigParser()
        config.read(localconfig)
        self.mode = config.get("Mode", "managermode", fallback="Yuzu")
        self.Yuzudir = None
        self.is_Ani_running = False
        self.root = window
        self.window = window
        self.title_id = title_id
        self.old_cheats = {}
        self.cheat_version = tk.StringVar(value="Version - 1.1.2")

        # Load Hover description locally.
        self.dfps_options = load_json("DFPS.json", dfpsurl)
        self.description = load_json("Description.json", descurl)
        self.presets = load_json("preset.json", presetsurl)
        self.version_options = load_json("Version.json", versionurl)
        self.cheat_options = load_json("Cheats.json", cheatsurl)

        # Warn for Backup File
        self.warnagain = "yes"

        # Local text variable
        self.switchtext = ttk.StringVar()
        self.switchtext.set("Switch to Ryujinx")

        # Load Canvas
        self.Load_ImagePath()
        self.load_canvas()
        self.allcanvas = [self.maincanvas, self.cheatcanvas]
        self.switchmode("false")
        # close existing threads.
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    # Canvas

    def createcanvas(self):
        # Create Canvas
        self.maincanvas = tk.Canvas(self.window, width= int(1200 * sf), height=int(600 * sf))
        self.maincanvas.pack()

        # Load UI Elements
        self.load_UI_elements(self.maincanvas)
        self.create_tab_buttons(self.maincanvas)

        # Create Text Position
        row = 40 * sf
        cultex = 40 * sf
        culsel = 180 * sf
        
        # Run Scripts for checking OS and finding location
        checkpath(self, self.mode)
        DetectOS(self, self.mode)
        # DEBUG purpose
        def onCanvasClick(event):
            print (f"CRODS = X={event.x} + Y={event.y} + {event.widget}")
        self.maincanvas.bind("<Button-3>", onCanvasClick)
        # Start of CANVAS options.
 
        # Create preset menu. 
        self.presets = {"Saved": {}} | self.presets
        self.preset_label = self.maincanvas.create_text(cultex+1, row+1, text="Select Preset:", anchor="w", fill=outlinecolor, font=textfont)
        self.preset_label2 = self.maincanvas.create_text(cultex, row, text="Select Preset:", anchor="w", fill=textcolor, font=textfont)
        self.selected_preset = tk.StringVar(value="Saved")
        self.preset_dropdown = ttk.Combobox(self.window, textvariable=self.selected_preset, values=list(self.presets.keys()))
        self.preset_dropdown_window = self.maincanvas.create_window(culsel, row, anchor="w", window=self.preset_dropdown)
        self.preset_dropdown.bind("<<ComboboxSelected>>", self.apply_selected_preset)
        self.read_description("Presets", self.preset_dropdown)


        # Setting Preset
        self.Settings_label_outline = self.maincanvas.create_text(370* sf+1, 40* sf+1, text="Yuzu Settings:", anchor="w", fill=outlinecolor, font=textfont)
        self.Settings_label = self.maincanvas.create_text(370* sf, 40* sf , text="Yuzu Settings:", anchor="w", fill=textcolor, font=textfont)
        self.selected_settings = tk.StringVar(value="No Change")
        self.second_dropdown = ttk.Combobox(self.window, textvariable=self.selected_settings, values=["No Change", "Steamdeck", "AMD", "Nvidia", "High End Nvidia"])
        self.second_dropdown_window = self.maincanvas.create_window(480* sf, 40 * sf, anchor="w", window=self.second_dropdown)
        self.second_dropdown.bind("<<ComboboxSelected>>")
        self.read_description("Settings", self.second_dropdown)
        row += 40* sf

        # Create a label for yuzu.exe selection
        backupbutton = culsel
        self.selectexe_outline = self.maincanvas.create_text(cultex+1, row+1, text="Select yuzu.exe:", anchor="w", fill=outlinecolor, font=textfont)
        self.selectexe = self.maincanvas.create_text(cultex, row, text="Select yuzu.exe:", anchor="w", fill=textcolor, font=textfont)
        if self.os_platform == "Windows":
            yuzu_button = ttk.Button(self.window, text="Browse", command=self.select_yuzu_exe)
            yuzu_button_window = self.maincanvas.create_window(culsel, row, anchor="w", window=yuzu_button)
            self.read_description("Browse", yuzu_button)

            # Reset to Appdata
            def yuzu_appdata():
                checkpath(self, self.mode)
                print("Successfully Defaulted to Appdata!")
                save_user_choices(self, self.config, "appdata", None)
            reset_button = ttk.Button(self.window, text="Use Appdata", command=yuzu_appdata)
            reset_button_window = self.maincanvas.create_window(culsel+70 * sf, row, anchor="w", window=reset_button)
            self.read_description("Reset", reset_button)
            backupbutton = culsel + 170* sf

        # Create a Backup button
        backup_button = ttk.Button(self.window, text="Backup", command=lambda: backup(self))
        backup_button_window = self.maincanvas.create_window(backupbutton, row, anchor="w", window=backup_button)
        self.read_description("Backup", backup_button)
        row += 40* sf

        # Create big TEXT label.
        self.preset_label = self.maincanvas.create_text(cultex+101* sf, row+1, text="Display Settings", anchor="w", fill=outlinecolor, font=bigfont)
        self.preset_label2 = self.maincanvas.create_text(cultex+100* sf, row, text="Display Settings", anchor="w", fill=BigTextcolor, font=bigfont)
        # Create big TEXT label.
        self.preset_label = self.maincanvas.create_text(400* sf+101* sf, row+1, text="Mod Improvements", anchor="w", fill=outlinecolor, font=bigfont)
        self.preset_label2 = self.maincanvas.create_text(400* sf+100* sf, row, text="Mod Improvements", anchor="w", fill=BigTextcolor, font=bigfont)

        row += 40* sf

        # Create a label for resolution selection
        self.maincanvas.create_text(cultex+1, row+1, text="Select a Resolution:", anchor="w", fill=outlinecolor, font=textfont)
        self.maincanvas.create_text(cultex, row, text="Select a Resolution:", anchor="w", fill=textcolor, font=textfont)
        self.resolution_var = tk.StringVar(value=self.dfps_options.get("ResolutionNames", [""])[2])  # Set the default resolution to "1080p FHD"
        resolution_dropdown = ttk.Combobox(self.window, textvariable=self.resolution_var, values=self.dfps_options.get("ResolutionNames", []))
        resolution_dropdown_window = self.maincanvas.create_window(culsel, row, anchor="w", window=resolution_dropdown)
        resolution_dropdown.bind("<<ComboboxSelected>>", lambda event: self.warning_window("Res"))
        self.read_description("Resolution", resolution_dropdown)
        row += 40* sf

        # Create a label for FPS selection
        self.maincanvas.create_text(cultex+1, row+1, text="Select an FPS:", anchor="w", fill=outlinecolor, font=textfont)
        self.maincanvas.create_text(cultex, row, text="Select an FPS:", anchor="w", fill=textcolor, font=textfont)
        self.fps_var = tk.StringVar(value=str(self.dfps_options.get("FPS", [])[2]))  # Set the default FPS to 60
        fps_dropdown = ttk.Combobox(self.window, textvariable=self.fps_var, values=self.dfps_options.get("FPS", []))
        fps_dropdown_window = self.maincanvas.create_window(culsel, row, anchor="w", window=fps_dropdown)
        self.read_description("FPS", fps_dropdown)
        row += 40* sf

        # Create a label for shadow resolution selection
        self.maincanvas.create_text(cultex+1, row+1, text="Shadow Resolution:", anchor="w", fill=outlinecolor, font=textfont)
        self.maincanvas.create_text(cultex, row, text="Shadow Resolution:", anchor="w", fill=textcolor, font=textfont)
        self.shadow_resolution_var = tk.StringVar(value=self.dfps_options.get("ShadowResolutionNames", [""])[0])  # Set the default shadow resolution to "Auto"
        shadow_resolution_dropdown = ttk.Combobox(self.window, textvariable=self.shadow_resolution_var, values=self.dfps_options.get("ShadowResolutionNames", []))
        shadow_resolution_dropdown_window = self.maincanvas.create_window(culsel, row, anchor="w", window=shadow_resolution_dropdown)
        self.read_description("Shadows", shadow_resolution_dropdown)
        row += 40* sf

        # Make exception for camera quality
        CameraQ = self.dfps_options.get("CameraQualityNames", [""])
        for index, value in enumerate(CameraQ):
            if value == "Enable" or value == "Enabled":
                CameraQ[index] = "On"
            elif value == "Disable" or value == "Disabled":
                CameraQ[index] = "Off"

        self.maincanvas.create_text(cultex+1, row+1, text="Camera Quality++:", anchor="w", fill=outlinecolor, font=textfont)
        self.maincanvas.create_text(cultex, row, text="Camera Quality++:", anchor="w", fill=textcolor, font=textfont)
        self.camera_var = tk.StringVar(value=CameraQ[0])  # Set the default camera quality to "Enable"
        camera_dropdown = ttk.Combobox(self.window, textvariable=self.camera_var, values=self.dfps_options.get("CameraQualityNames", []))
        camera_dropdown_window = self.maincanvas.create_window(culsel, row, anchor="w", window=camera_dropdown)
        self.read_description("Camera Quality", camera_dropdown)
        row += 40* sf

        # Create a label for UI selection
        
        self.maincanvas.create_text(cultex+1, row+1, text="Select an UI:", anchor="w", fill=outlinecolor, font=textfont)
        self.maincanvas.create_text(cultex, row, text="Select an UI:", anchor="w", fill=textcolor, font=textfont)
        ui_values = ["None", "Black Screen Fix", "PS4", "Xbox"]
        self.ui_var = tk.StringVar(value=ui_values[0])
        ui_dropdown = ttk.Combobox(self.window, textvariable=self.ui_var, values=ui_values)
        ui_dropdown_window = self.maincanvas.create_window(culsel, row, anchor="w", window=ui_dropdown)
        self.read_description("UI", ui_dropdown)
        row += 40* sf

        # First Person and FOV
        self.maincanvas.create_text(cultex+1, row+1, text="Enable First Person:", anchor="w", fill=outlinecolor, font=textfont)
        self.maincanvas.create_text(cultex, row, text="Enable First Person:", anchor="w", fill=textcolor, font=textfont)
        fp_values = ["Off", "70 FOV", "90 FOV", "110 FOV"]
        self.fp_var = tk.StringVar(value=ui_values[0])
        fp_dropdown = ttk.Combobox(self.window, textvariable=self.fp_var, values=fp_values)
        fp_dropdown_window = self.maincanvas.create_window(culsel, row, anchor="w", window=fp_dropdown)
        self.read_description("First Person", fp_dropdown)
        
        # XYZ to generate patch.

        row = 120 * sf
        cultex = 400 * sf
        culsel = 550 * sf

        # Create labels and enable/disable options for each entry
        self.selected_options = {}
        for version_option_name, version_option_value in self.version_options[0].items():

            # Create label
            if version_option_name not in ["Source", "nsobid", "offset", "version"]:
                self.maincanvas.create_text(cultex+1, row+40 * sf+1, text=version_option_name, anchor="w", fill=outlinecolor, font=textfont)
                self.maincanvas.create_text(cultex, row+40 * sf, text=version_option_name, anchor="w", fill=textcolor, font=textfont)
                    

                # Create checkbox
                version_option_var = tk.StringVar(value="Off")
                versioncheck = ttk.Checkbutton(self.window, variable=version_option_var, onvalue="On", offvalue="Off", bootstyle="success")
                version_check_window = self.maincanvas.create_window(culsel, row+40 * sf, anchor="w", window=versioncheck)
                self.read_description(f"{version_option_name}", versioncheck)
                self.selected_options[version_option_name] = version_option_var
                row += 40 * sf

            if row >= 480 * sf:
                row = 120 * sf
                cultex += 180 * sf
                culsel += 180 * sf

        # Create a submit button
        submit_button = ttk.Button(self.window, text="Apply Mods", command=self.submit, padding=5, bootstyle="success")
        submit_button_window = self.maincanvas.create_window(39 * sf, 520 * sf, anchor="w", window=submit_button)
        self.read_description("Apply", submit_button)

        # Load Saved User Options.
        load_user_choices(self, self.config)
        return self.maincanvas

    def createcheatcanvas(self):
        # Create Cheat Canvas
        self.cheatcanvas = tk.Canvas(self.window, width=1200 * sf, height=600 * sf)
        self.cheatcanvas.pack(expand=1, fill=BOTH)

        # Create UI elements.
        self.Cheat_UI_elements(self.cheatcanvas)
        self.create_tab_buttons(self.cheatcanvas)

        # Create Positions.
        row = 40 * sf
        cultex = 40 * sf
        culsel = 200 * sf
        Hoverdelay = 500 * sf

        # Push every version in combobox
        versionvalues = []
        for each in self.cheat_options:
            for key, value in each.items():
                if key == "Aversion":
                    versionvalues.append("Version - " + value)
        
        self.cheat_version_dropdown = ttk.Combobox(self.window, textvariable=self.cheat_version, values=versionvalues)
        self.cheat_version_dropdown_window = self.cheatcanvas.create_window(130 * sf, 520 * sf, anchor="w", window=self.cheat_version_dropdown)
        self.cheat_version_dropdown.bind("<<ComboboxSelected>>", lambda event: loadCheats())


        def loadCheats():
            
            row = 40 * sf
            cultex = 40 * sf
            culsel = 200 * sf
            Hoverdelay = 500 * sf
            
            corrent_cheats = self.cheat_options[versionvalues.index(self.cheat_version.get())].items()
            corrent_cheats_dict = dict(corrent_cheats)
            sorted_cheats = dict(sorted(corrent_cheats_dict.items(), key=lambda item: item[0]))
            try:
                for key_var, value in self.selected_cheats.items():
                    value = value.get()
                    self.old_cheats[key_var] = value
            except AttributeError as e:
                self.old_cheats = {}

            self.selected_cheats = {}

            self.cheatcanvas.delete("cheats")

            for version_option_name, version_option_value in sorted_cheats.items():
                # Exclude specific keys from being displayed
                if version_option_name in ["Source", "nsobid", "offset", "version"]:
                    continue

                # Create label
                if version_option_name not in ["Source", "Version", "Aversion", "Cheat Example"]:
                    self.cheatcanvas.create_text(cultex+1, row+1, text=version_option_name, anchor="w", fill=outlinecolor, font=textfont, tags="cheats")
                    self.cheatcanvas.create_text(cultex, row, text=version_option_name, anchor="w", fill=textcolor, font=textfont, tags="cheats")
                    # Create enable/disable dropdown menu
                    version_option_var = tk.StringVar(value="Off")
                    try:
                        if self.old_cheats.get(version_option_name) == "On":
                            version_option_var.set("On")
                    except AttributeError as e:
                        self.old_cheats = {}

                    versioncheck = ttk.Checkbutton(self.window, variable=version_option_var, onvalue="On", offvalue="Off", bootstyle="success")
                    version_check_window = self.cheatcanvas.create_window(culsel, row, anchor="w", window=versioncheck, tags="cheats")

                    self.selected_cheats[version_option_name] = version_option_var

                else:
                    continue

                if version_option_name in self.description:
                    hover = self.description[version_option_name]
                    versionhover = Hovertip(versioncheck, f"{hover}", hover_delay=Hoverdelay)

                row += 40 * sf

                if row >= 520 * sf:
                    row = 40 * sf
                    cultex += 200 * sf
                    culsel += 200 * sf
        def ResetCheats():
            try:
                for key, value in self.selected_cheats.items():
                    value.set("Off")
            except AttributeError as e:
                print(e)
                print("Error found from ResetCheats, the script will continue.")

        
        # Create a submit button
        submit_button = ttk.Button(self.window, text="Apply Cheats", command=lambda: self.submit("Cheats"), padding=5)
        submit_button_window = self.cheatcanvas.create_window(39 * sf, 520 * sf, anchor="w", window=submit_button)
        self.read_description("Apply", submit_button)

        # Create a submit button
        resetcheats_button = ttk.Button(self.window, text="Reset Cheats", command=lambda: ResetCheats(), padding=5)
        resetcheats_button_window = self.cheatcanvas.create_window(280* sf+ 6 * sf, 520* sf, anchor="w", window=resetcheats_button)
        self.read_description("Reset Cheats", submit_button)
        # Read Cheats

        readcheats_button = ttk.Button(self.window, text="Read Saved Cheats", command=lambda: load_user_choices(self, self.config, "Cheats"), padding=5)
        readcheats_button_window = self.cheatcanvas.create_window(370* sf +6 * sf, 520* sf, anchor="w", window=readcheats_button)
        self.read_description("Read Cheats", submit_button)

        #Backup
        backup_button = ttk.Button(self.window, text="Backup", command=lambda: backup(self))
        backup_button_window = self.cheatcanvas.create_window(490* sf+8* sf, 520* sf, anchor="w", window=backup_button)
        self.read_description("Backup", backup_button)

        loadCheats()
        load_user_choices(self, self.config)

    def show_maincanvas(self):
        self.cheatcanvas.pack_forget()
        self.maincanvas.pack()
        def canvasanimation():
            for x in range(1000):
                self.cheatcanvas.move(self.cheatbg, -0.5* sf, 0)
                time.sleep(0.02)
            else:
                self.cheatcanvas.move(self.cheatbg, 200* sf, 200* sf)
                for y in range(250):
                    self.cheatcanvas.move(self.cheatbg, 0, -0.5* sf)
                    time.sleep(0.02)

    def show_cheatcanvas(self):
        self.cheatcanvas.pack()
        self.maincanvas.pack_forget()
        def canvasanimation():
            if not self.is_Ani_running == True:
                return
            for x in range(1000):
                self.cheatcanvas.move(self.cheatbg, -1* sf, 0)
                time.sleep(0.05)
                if not self.is_Ani_running == True:
                    return
            else:
                self.cheatcanvas.move(self.cheatbg, 200* sf, 200* sf)
                for y in range(250):
                    self.cheatcanvas.move(self.cheatbg, 0, -1)
                    time.sleep(0.05)
                    if not self.is_Ani_running == True:
                        return
                else:
                    self.cheatcanvas.move(self.cheatbg, 800* sf, 50* sf)
                    canvasanimation()
        self.ani = threading.Thread(name="cheatbackground", target=canvasanimation)
        if not self.is_Ani_running == True:
            self.is_Ani_running = True
            self.ani.start()

    def open_browser(self, web, event=None):

        url = "https://ko-fi.com/maxlastbreath#"

        if web == "Kofi":
            url = "https://ko-fi.com/maxlastbreath#"
        elif web == "Github":
            url = "https://github.com/MaxLastBreath/TOTK-mods"
        elif web == "Discord":
            url = "https://discord.gg/7MMv4yGfhM"

        webbrowser.open(url)
        return

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

    def load_canvas(self):
        # Main
        self.createcanvas()
        self.createcheatcanvas()
        self.cheatcanvas.pack_forget()

    def Load_ImagePath(self):
        # Create a Gradiant for Yuzu.
        UI_path = self.get_UI_path("Yuzu_BG.png")
        image = Image.open(UI_path)
        image = image.resize((1200 * sf, 600 * sf))
        self.background_YuzuBG = ImageTk.PhotoImage(image)

        # Create a Gradiant for Ryujinx.
        UI_path = self.get_UI_path("Ryujinx_BG.png")
        image = Image.open(UI_path)
        image = image.resize((1200 * sf, 600 * sf))
        self.background_RyuBG = ImageTk.PhotoImage(image)
        # UI Elements
        UI_path = self.get_UI_path("Master_Sword.png")
        image = Image.open(UI_path)
        image = image.resize((155 * sf, 88 * sf))
        self.master_sword_element = ImageTk.PhotoImage(image)

        UI_path = self.get_UI_path("Master_Sword_active.png")
        image = Image.open(UI_path)
        image = image.resize((155 * sf, 88 * sf))
        self.master_sword_element_active = ImageTk.PhotoImage(image)

        UI_path = self.get_UI_path("Master_Sword2.png")
        image = Image.open(UI_path)
        image = ImageOps.mirror(image)
        image = image.resize((155 * sf, 88 * sf))
        self.master_sword_element2 = ImageTk.PhotoImage(image)

        UI_path = self.get_UI_path("Master_Sword_active2.png")
        image = Image.open(UI_path)
        image = ImageOps.mirror(image)
        image = image.resize((155 * sf, 88 * sf))
        self.master_sword_element2_active = ImageTk.PhotoImage(image)

        UI_path = self.get_UI_path("Hylian_Shield.png")
        image = Image.open(UI_path)
        image = image.resize((72 * sf, 114 * sf))
        self.hylian_element = ImageTk.PhotoImage(image)

        UI_path = self.get_UI_path("Hylian_Shield_active.png")
        image = Image.open(UI_path)
        image = image.resize((72 * sf, 114 * sf))
        self.hylian_element_active = ImageTk.PhotoImage(image)


        # Create a Gradiant background.
        UI_path = self.get_UI_path("BG_Left.png")
        image = Image.open(UI_path)
        image = image.resize((1200 * sf, 600 * sf))
        self.background_UI = ImageTk.PhotoImage(image)

        UI_path = self.get_UI_path("BG_Left_2.png")
        image = Image.open(UI_path)
        image = image.resize((1200 * sf, 600 * sf))
        self.background_UI_element = ImageTk.PhotoImage(image)

        # Create Gradiant for cheats.
        UI_path = self.get_UI_path("BG_Cheats.png")
        image = Image.open(UI_path)
        image = image.resize((1200 * sf, 600 * sf))
        self.background_Cheats = ImageTk.PhotoImage(image)

        # Create a transparent black background
        UI_path2 = self.get_UI_path("BG_Right.png")
        image = Image.open(UI_path2)
        image = image.resize((1200 * sf, 600 * sf))
        self.background_UI2 = ImageTk.PhotoImage(image)

        # Create a transparent black background
        UI_path2 = self.get_UI_path("BG_Right_UI.png")
        image = Image.open(UI_path2)
        image = image.resize((1200 * sf, 600 * sf))
        self.background_UI3 = ImageTk.PhotoImage(image)

        # Load and set the image as the background
        image_path = self.get_UI_path("image.png")
        image = Image.open(image_path)
        image = image.resize((1200 * sf, 600 * sf))
        image = image.filter(ImageFilter.GaussianBlur(1))
        self.background_image = ImageTk.PhotoImage(image)

        image_path = self.get_UI_path("image.png")
        image = Image.open(image_path)
        image = image.resize((2400 * sf, 1200 * sf))
        image = image.filter(ImageFilter.GaussianBlur(3))
        self.blurbackground = ImageTk.PhotoImage(image)

        # Handle Text Window
        def fetch_text_from_github(file_url):
            try:
                response = requests.get(file_url)
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"Error: Unable to fetch text from Github")
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while fetching text: {e}")

            return ""
        # Information text
        file_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/Announcements/Announcement%20Window.txt"
        self.text_content = fetch_text_from_github(file_url)
        # Info Element

    def hoveranimation(self, canvas, mode, element, event):
        if mode.lower() == "enter":
            if element.lower() == "kofi":
                canvas.itemconfig(self.mastersword, state="hidden")
                canvas.itemconfig(self.mastersword_active, state="normal")
            if element.lower() == "github":
                canvas.itemconfig(self.mastersword1, state="hidden")
                canvas.itemconfig(self.mastersword1_active, state="normal")
            if element.lower() == "discord":
                canvas.itemconfig(self.hylian, state="hidden")
                canvas.itemconfig(self.hylian_active, state="normal")

        if mode.lower() == "leave":
            if element.lower() == "kofi":
                canvas.itemconfig(self.mastersword, state="normal")
                canvas.itemconfig(self.mastersword_active, state="hidden")
            if element.lower() == "github":
                canvas.itemconfig(self.mastersword1, state="normal")
                canvas.itemconfig(self.mastersword1_active, state="hidden")
            if element.lower() == "discord":
                canvas.itemconfig(self.hylian, state="normal")
                canvas.itemconfig(self.hylian_active, state="hidden")

    def load_UI_elements(self, canvas):
        # Images and Effects
        
        canvas.create_image(0, 0, anchor="nw", image=self.background_image, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_YuzuBG, tags="overlay-1")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI, tags="overlay")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI_element, tags="overlay")
        # Info text BG
        canvas.create_image(0-20* sf, 0, anchor="nw", image=self.background_UI2, tags="overlay")
        canvas.create_image(0-20* sf, 0, anchor="nw", image=self.background_UI3, tags="overlay")

        # Trigger Animation
        self.mastersword = canvas.create_image(794* sf, 222* sf-40* sf, anchor="nw", image=self.master_sword_element, tags="overlay-sword1")
        self.mastersword_active = canvas.create_image(794* sf, 222* sf-40* sf, anchor="nw", image=self.master_sword_element_active, tags="overlay-sword1")
        self.maincanvas.itemconfig(self.mastersword_active, state="hidden")

        canvas.tag_bind(self.mastersword, "<Enter>", lambda event: self.hoveranimation(canvas, "Enter", "Kofi", event))
        canvas.tag_bind(self.mastersword_active, "<Leave>", lambda event: self.hoveranimation(canvas, "Leave", "Kofi", event))
        canvas.tag_bind(self.mastersword_active, "<Button-1>", lambda event: self.open_browser("Kofi"))

        # Trigger Animation
        self.mastersword1 = canvas.create_image(1007* sf, 222* sf-40* sf, anchor="nw", image=self.master_sword_element2, tags="overlay-sword2")
        self.mastersword1_active = canvas.create_image(1007* sf, 222* sf-40* sf, anchor="nw", image=self.master_sword_element2_active, tags="overlay-sword2")
        self.maincanvas.itemconfig(self.mastersword1_active, state="hidden")

        canvas.tag_bind(self.mastersword1, "<Enter>", lambda event: self.hoveranimation(canvas, "Enter", "Github", event))
        canvas.tag_bind(self.mastersword1_active, "<Leave>", lambda event: self.hoveranimation(canvas, "Leave", "Github", event))
        canvas.tag_bind(self.mastersword1_active, "<Button-1>", lambda event: self.open_browser("Github"))

        # Hylian Shield
        self.hylian = canvas.create_image(978* sf, 240* sf, anchor="c", image=self.hylian_element, tags="overlay-hylian")
        self.hylian_active = canvas.create_image(978* sf, 240* sf, anchor="c", image=self.hylian_element_active, tags="overlay")
        self.maincanvas.itemconfig(self.hylian_active, state="hidden")
        canvas.tag_bind(self.hylian, "<Enter>", lambda event: self.hoveranimation(canvas, "Enter", "discord", event))
        canvas.tag_bind(self.hylian_active, "<Leave>", lambda event: self.hoveranimation(canvas, "Leave", "discord", event))
        canvas.tag_bind(self.hylian_active, "<Button-1>", lambda event: self.open_browser("Discord"))

        biggyfont = ("Arial Bold", 14, "bold")
        if sf > 1:
            biggyfont = ("Arial Bold", 11, "bold")

        # Information text.
        text_widgetoutline2 = canvas.create_text(1001* sf-20* sf, 126* sf -80* sf, text=f"{self.mode} TOTK Optimizer", tags="information", fill="black", font=biggyfont, anchor="center", justify="center", width=325* sf)
        text_widget2 = canvas.create_text(1000* sf-20* sf, 126* sf-80 * sf, text=f"{self.mode} TOTK Optimizer", tags="information", fill="#FBF8F3", font=biggyfont, anchor="center", justify="center", width=325* sf)
 
        text_widgetoutline1 = canvas.create_text(1001 * sf -20 * sf-10 * sf, 126 * sf +10 * sf, text=self.text_content, fill="black", font=biggyfont, anchor="center", justify="center", width=325* sf)
        text_widget1 = canvas.create_text(1000 * sf-20* sf-10* sf, 125* sf +10 * sf, text=self.text_content, fill="#FBF8F3", font=biggyfont, anchor="center", justify="center", width=325* sf)

    def Cheat_UI_elements(self, canvas):
        self.cheatbg = canvas.create_image(0, -300* sf, anchor="nw", image=self.blurbackground, tags="background")
        canvas.create_image(0, 0, anchor="nw", image=self.background_YuzuBG, tags="overlay-1")
        canvas.create_image(0, 0, anchor="nw", image=self.background_UI, tags="overlay")

    def create_tab_buttons(self, canvas):
        # GitHub Button

        # Ko-fi Button
        def enter(event, tag):
            self.maincanvas.itemconfigure(tag, fill="red")
        def leave(event, tag):
            self.maincanvas.itemconfigure(tag, fill=textcolor)

        if not canvas == self.maincanvas:
            kofi_button = ttk.Button(self.window, text="Donate", bootstyle="success", command=lambda: self.open_browser("Kofi"), padding=10)
            kofi_button_window = canvas.create_window(1110* sf+20* sf, 520* sf, anchor="center", window=kofi_button)
            self.read_description("Kofi", kofi_button)
            github_button = ttk.Button(self.window, text="Github", bootstyle="info", command=lambda: self.open_browser("Github"), padding=10)
            github_button_window = canvas.create_window(1046* sf+20* sf, 520* sf, anchor="center", window=github_button)
            self.read_description("Github", github_button)



        # Create tabs
        cul = 10

        # Switch mode between Ryujinx and Yuzu
        manager_switch = ttk.Button(self.window, textvariable=self.switchtext, command=self.switchmode, bootstyle=style)
        manager_switch_window = canvas.create_window(114* sf + 43* sf - 17* sf, cul, anchor="w", window=manager_switch)
        self.read_description("Switch", manager_switch)

        # Make the button active for current canvas.
        button1style = "default"
        button2style = "default"
        active_button_style = "secondary"
        try:
            if canvas == self.maincanvas:
                button1style = active_button_style
        except AttributeError as e:
            print("")
        try:
            if canvas == self.cheatcanvas:
                button2style = active_button_style
        except AttributeError as e:
            print("")

        # 1
        self.tab1_button = ttk.Button(self.window, text="Main", bootstyle=f"{button1style}", command=self.show_maincanvas)
        tab1_button_window = canvas.create_window(0+ 43* sf - 17* sf, cul, anchor="w", window=self.tab1_button)
        self.read_description("Main", self.tab1_button)
        # 2
        self.tab2_button = ttk.Button(self.window, text="Cheats", bootstyle=f"{button2style}", command=self.show_cheatcanvas)
        tab2_button_window = canvas.create_window(52* sf+ 43* sf - 17* sf, cul, anchor="w", window=self.tab2_button)
        self.read_description("Cheats", self.tab2_button)

    def switchmode(self, command="true"):
        if command == "true":
            if self.mode == "Yuzu":
                self.mode = "Ryujinx"
                for canvas in self.allcanvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                self.switchtext.set("Switch to Yuzu")
                self.maincanvas.itemconfig(self.Settings_label_outline, text="")
                self.maincanvas.itemconfig(self.Settings_label, text="")
                self.maincanvas.itemconfig(self.selectexe_outline, text="Select Ryujinx.exe")
                self.maincanvas.itemconfig(self.selectexe, text="Select Ryujinx.exe")
                self.second_dropdown.destroy()
                return
            elif self.mode == "Ryujinx":
                self.mode = "Yuzu"
                for canvas in self.allcanvas:
                    canvas.itemconfig("overlay-1", image=self.background_YuzuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                # change text
                self.switchtext.set("Switch to Ryujinx")
                self.maincanvas.itemconfig(self.Settings_label_outline, text="Yuzu Settings:")
                self.maincanvas.itemconfig(self.Settings_label, text="Yuzu Settings:")
                self.maincanvas.itemconfig(self.selectexe_outline, text="Select yuzu.exe")
                self.maincanvas.itemconfig(self.selectexe, text="Select yuzu.exe")

                # create new labels
                self.selected_settings = tk.StringVar(value="No Change")
                self.second_dropdown = ttk.Combobox(self.window, textvariable=self.selected_settings, values=["No Change", "Steamdeck", "AMD", "Nvidia", "High End Nvidia"])
                self.second_dropdown_window = self.maincanvas.create_window(470* sf, 40* sf, anchor="w", window=self.second_dropdown)
                self.second_dropdown.bind("<<ComboboxSelected>>")
                return
        elif command == "false":
            if self.mode == "Ryujinx":
                for canvas in self.allcanvas:
                    canvas.itemconfig("overlay-1", image=self.background_RyuBG)
                    canvas.itemconfig("information", text=f"{self.mode} TOTK Optimizer")
                self.switchtext.set("Switch to Yuzu")
                self.maincanvas.itemconfig(self.Settings_label_outline, text="")
                self.maincanvas.itemconfig(self.Settings_label, text="")
                self.maincanvas.itemconfig(self.selectexe_outline, text="Select Ryujinx.exe")
                self.maincanvas.itemconfig(self.selectexe, text="Select Ryujinx.exe")
                self.second_dropdown.destroy()
                return
        elif command == "Mode":
            return self.mode
    # Read Hover Description
    def read_description(self, option, position):
        if f"{option}" in self.description:
            hover = self.description[f"{option}"]
            Hovertip(position, f"{hover}", hover_delay=Hoverdelay)

    def apply_selected_preset(self, event=None):
        selected_preset = self.selected_preset.get()

        if selected_preset == "None":
            if os.path.exists(self.config):
                load_user_choices(self, self.config)
            else:
                # Fallback to the default preset
                default_preset = self.get_local_presets().get("Default", {})
                self.apply_preset(default_preset)
        
        elif selected_preset == "Saved":
            if os.path.exists(self.config):
                load_user_choices(self, self.config)
            else:
                messagebox.showinfo("Saved Preset", "No saved preset found. Please save your current settings first.")
        elif selected_preset in self.presets:
            preset_to_apply = self.presets[selected_preset]
            for key, value in preset_to_apply.items():
                if value == "Enable":
                    preset_to_apply[key] = "On"
                if value == "Enabled":
                    preset_to_apply[key] = "On"
                elif value == "Disable":
                    preset_to_apply[key] = "Off"
                elif value == "Disabled":
                    preset_to_apply[key] = "Off"
            # Apply the selected preset from the online presets
            self.apply_preset(self.presets[selected_preset])

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
            Default_Yuzu_Directory = os.path.join(home_directory, "user")
            Default_Ryujinx_Directory = os.path.join(home_directory, "portable")
            executablename = yuzu_path
            if executablename.endswith("Ryujinx.exe"):
                if self.mode == "Yuzu":
                    self.switchmode("true")
            if executablename.endswith("yuzu.exe"):
                if self.mode == "Ryujinx":
                    self.switchmode("true")
            if yuzu_path:
                # Save the selected yuzu.exe path to a configuration file
                save_user_choices(self, self.config, yuzu_path)
                home_directory = os.path.dirname(yuzu_path)
                if os.path.exists(Default_Yuzu_Directory) or os.path.exists(Default_Ryujinx_Directory):
                    print(f"Successfully selected {self.mode}.exe! And a portable folder was found at {home_directory}!")
                    checkpath(self, self.mode)
                else:
                    print("Portable folder not found defaulting to default appdata directory!")
                    checkpath(self, self.mode)

                # Update the yuzu.exe path in the current session
                self.yuzu_path = yuzu_path
            else:
                checkpath(self, self.mode)
            # Save the selected yuzu.exe path to a configuration file
            save_user_choices(self, self.config, yuzu_path) 
        return
    # Load Yuzu Dir
    def load_yuzu_path(self, config_file):
        if self.mode == "Yuzu":
            config = configparser.ConfigParser()
            config.read(config_file)
            yuzu_path = config.get('Paths', 'YuzuPath', fallback="Appdata")
            return yuzu_path
        if self.mode == "Ryujinx":
            config = configparser.ConfigParser()
            config.read(config_file)
            ryujinx_path = config.get('Paths', 'RyujinxPath', fallback="Appdata")
            return ryujinx_path
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

    def on_closing(self):
        print("Closing Window")
        self.is_Ani_running = False
        self.window.destroy()
    # Submit the results, run download manager. Open a Loading screen.
    def submit(self, mode=None):
        checkpath(self, self.mode)
        def timer(value):
            progress_bar["value"] = value
            self.window.update_idletasks()
        def run_tasks():
            if mode== "Cheats":
                timer(50)
                print(f"Backing up TOTK, save file from {self.nand_dir}.")
                backup(self)
                time.sleep(0.3)
                timer(100)
                UpdateVisualImprovements("Cheats")
                progress_window.destroy()
                return
            if mode== None:
                timer(20)
                DownloadFP()
                timer(40)
                DownloadUI()
                timer(50)
                DownloadDFPS()
                timer(80)
                UpdateVisualImprovements()
                time.sleep(0.3)
                timer(100)
                UpdateSettings()
                progress_window.destroy()
                return

        def UpdateVisualImprovements(mode=None):
            save_user_choices(self, self.config)

            if mode == "Cheats":
                save_user_choices(self, self.config, None, "Cheats")
                selected_cheats = {}
                for option_name, option_var in self.selected_cheats.items():
                    selected_cheats[option_name] = option_var.get()
                # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Yuzu together.
                for version_option in self.cheat_options:
                    version = version_option.get("Version", "")
                    mod_path = os.path.join(self.load_dir, "Cheat Manager Patch", "cheats")

                    # Create the directory if it doesn't exist
                    os.makedirs(mod_path, exist_ok=True)

                    filename = os.path.join(mod_path, f"{version}.txt")
                    all_values = []
                    with open(filename, "w") as file:
                        # file.write(version_option.get("Source", "") + "\n") - makes cheats not work
                        for key, value in version_option.items():
                            if key in selected_cheats:
                                if key not in ["Source", "Aversion", "Version"] and selected_cheats[key] == "On":
                                    file.write(value + "\n")
                print("Applied cheats.")
                return

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
            Resindex = self.dfps_options.get("ResolutionNames").index(resolution)
            ShadowIndex = self.dfps_options.get("ShadowResolutionNames").index(shadow_resolution)
            CameraIndex = self.dfps_options.get("CameraQualityNames").index(camera_quality)

            config['Graphics'] = {
                'ResolutionWidth': self.dfps_options.get("ResolutionValues", [""])[Resindex].split("x")[0],
                'ResolutionHeight': self.dfps_options.get("ResolutionValues", [""])[Resindex].split("x")[1],
                'ResolutionShadows': self.dfps_options.get("ShadowResolutionValues", [""])[ShadowIndex]
            }
            config['dFPS'] = {'MaxFramerate': fps}
            config['Features'] = {'EnableCameraQualityImprovement': self.dfps_options.get("CameraQualityValues", [""])[CameraIndex]}

            selected_options = {}

            for option_name, option_var in self.selected_options.items():
                selected_options[option_name] = option_var.get()
            # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Yuzu together.
            for version_option in self.version_options:
                version = version_option.get("version", "")
                mod_path = os.path.join(self.load_dir, "Mod Manager Patch", "exefs")

                # Create the directory if it doesn't exist
                os.makedirs(mod_path, exist_ok=True)

                filename = os.path.join(mod_path, f"{version}.pchtxt")
                all_values = []
                with open(filename, "w") as file:
                    file.write(version_option.get("Source", "") + "\n")
                    file.write(version_option.get("nsobid", "") + "\n")
                    file.write(version_option.get("offset", "") + "\n")
                    for key, value in version_option.items():
                        if key not in ["Source", "nsobid", "offset", "version", "Version"] and self.selected_options[key].get() == "On":
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
            if self.mode == "Yuzu":
                qtconfig = get_config_parser()
                qtconfig.optionxform = lambda option: option
                qtconfig.read(self.configdir)
            else:
                qtconfig = None
            # Ensures that the patches are active
            modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "DFPS", action="remove")
            modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Mod Manager Patches", action="remove")
            # To maximize compatbility with old version of Mod Folders and Mod Manager.
            modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Visual Improvements", action="add")
            # Update Visual Improvements MOD.
            with open(ini_file_path, 'w') as configfile:
                config.write(configfile)

        def UpdateSettings():
            Setting_folder = None
            SettingGithubFolder = None
            Setting_selection = self.selected_settings.get()
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
                        resolution = self.resolution_var.get()
                        Resindex = self.dfps_options.get("ResolutionNames").index(resolution)
                        current_res = self.dfps_options.get("ResolutionValues", [""])[Resindex].split("x")[1]
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
            # Make sure DFPS is enabled.
            if self.mode == "Yuzu":
                qtconfig = get_config_parser()
                qtconfig.optionxform = lambda option: option
                qtconfig.read(self.configdir)
            else:
                qtconfig = None
            modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "DFPS", action="remove")

            config = configparser.ConfigParser()
            config.read(self.config)
            if not config.has_section("Updates"):
                config.add_section("Updates")
                config.set("Updates", "dfps", "1.0.0")
                with open(self.config, "w") as configfile:
                    config.write(configfile)
            try:
                latest_dfps_version = config.get("Updates", "dfps")
            except NoOptionError as e:
                # Handle the case when "dfps" option doesn't exist
                config.set("Updates", "dfps", "1.0.0")
                with open(self.config, "w") as configfile:
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
                with open(self.config, "w") as configfile:
                    config.write(configfile)
            else:
                print("You already have the latest DFPS version and the folder exists!")

        def DownloadUI():
            if self.mode == "Yuzu":
                qtconfig = get_config_parser()
                qtconfig.optionxform = lambda option: option
                qtconfig.read(self.configdir)
            else:
                qtconfig = None
            #dirs
            Blackscreen = os.path.join(self.load_dir, "BlackscreenFIX")
            Xbox = os.path.join(self.load_dir, "Xbox UI")
            Ps4 = os.path.join(self.load_dir, "Playstation UI")
            #ui
            ui_mod_folder = None
            CurrentFolder = None
            ui_selection = self.ui_var.get()
            print(f"{self.fp_var.get()}")
            if ui_selection == "None":
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Xbox UI", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Playstation UI", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "BlackscreenFix", action="add")
                if self.mode == "Ryujinx":
                    if os.path.exists(Ps4):
                       shutil.rmtree(Ps4)
                    if os.path.exists(Blackscreen):
                       shutil.rmtree(Blackscreen)
                    if os.path.exists(Xbox):
                       shutil.rmtree(Xbox)
                print("No UI Selected, Disabling all UI mods!")
            elif ui_selection == "PS4":
                if self.mode == "Ryujinx":
                    if os.path.exists(Xbox):
                       shutil.rmtree(Xbox)
                    if os.path.exists(Blackscreen):
                       shutil.rmtree(Blackscreen)
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Xbox UI", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "BlackscreenFix", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Playstation UI", action="remove")
                ui_mod_folder = "Playstation UI"
                CurrentFolder = "scripts/UI/Playstation%20UI/"
            elif ui_selection == "Xbox":
                if self.mode == "Ryujinx":
                    if os.path.exists(Ps4):
                       shutil.rmtree(Ps4)
                    if os.path.exists(Blackscreen):
                       shutil.rmtree(Blackscreen)
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Playstation UI", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "BlackscreenFix", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Xbox UI", action="remove")
                ui_mod_folder = "Xbox UI"
                CurrentFolder = 'scripts/UI/Xbox%20UI/'
            elif ui_selection == "Black Screen Fix":
                if self.mode == "Ryujinx":
                    if os.path.exists(Ps4):
                       shutil.rmtree(Ps4)
                    if os.path.exists(Xbox):
                       shutil.rmtree(Xbox)
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Playstation UI", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "Xbox UI", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "BlackscreenFix", action="remove")
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
            if self.mode == "Yuzu":
                qtconfig = get_config_parser()
                qtconfig.optionxform = lambda option: option
                qtconfig.read(self.configdir)
            else:
                qtconfig = None

            FP_mod_folder = None
            FPCurrentFolder = None
            FP_selection = self.fp_var.get()
            fov70 = os.path.join(self.load_dir, "First Person 70 FOV")
            fov90 = os.path.join(self.load_dir, "First Person 90 FOV")
            fov110 = os.path.join(self.load_dir, "First Person 110 FOV")
            if FP_selection == "Off":
                if self.mode == "Ryujinx":
                    if os.path.exists(fov70):
                       shutil.rmtree(fov70)
                    if os.path.exists(fov90):
                       shutil.rmtree(fov90)
                    if os.path.exists(fov110):
                       shutil.rmtree(fov110)
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 110 FOV", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 90 FOV", action="add")
                modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 70 FOV", action="add")
                print("Selected Third Person, removing ALL First Person Mods!")

            elif FP_selection == "70 FOV":
                    FP_mod_folder = "First Person 70 FOV"
                    FPCurrentFolder = "scripts/UI/First%20Person%20FOV%2070/"
                    if self.mode == "Ryujinx":
                        if os.path.exists(fov90):
                            shutil.rmtree(fov90)
                        if os.path.exists(fov110):
                            shutil.rmtree(fov110)
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 110 FOV", action="add")
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 90 FOV", action="add")
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 70 FOV", action="remove")

            elif FP_selection == "90 FOV":
                    FP_mod_folder = "First Person 90 FOV"
                    FPCurrentFolder = 'scripts/UI/First%20Person%20FOV%2090/'
                    if self.mode == "Ryujinx":
                        if os.path.exists(fov70):
                            shutil.rmtree(fov70)
                        if os.path.exists(fov110):
                            shutil.rmtree(fov110)
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 110 FOV", action="add")
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 70 FOV", action="add")
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 90 FOV", action="remove")

            elif FP_selection == "110 FOV":
                    FP_mod_folder = "First Person 110 FOV"
                    FPCurrentFolder = 'scripts/UI/First%20Person%20FOV%20110/'
                    if self.mode == "Ryujinx":
                        if os.path.exists(fov70):
                            shutil.rmtree(fov70)
                        if os.path.exists(fov90):
                            shutil.rmtree(fov90)
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 70 FOV", action="add")
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 90 FOV", action="add")
                    modify_disabled_key(self.configdir, self.load_dir, qtconfig, self.title_id, "First Person 100 FOV", action="remove")

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
        progress_window.resizable(False, False)
        total_iterations = 100
        progress_bar = ttk.Progressbar(progress_window, mode="determinate", maximum=total_iterations)
        progress_bar.pack(pady=20)
        task_thread = threading.Thread(target=run_tasks)
        task_thread.start()