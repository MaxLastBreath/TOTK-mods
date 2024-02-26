from modules.checkpath import checkpath
from configuration.settings import *
import os, json, uuid

def save_user_choices(self, config_file, yuzu_path=None, mode=None):
    log.info(f"Saving user choices in {localconfig}")
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)

    if mode == "Cheats":
        config["Cheats"] = {}
        for option_name, option_var in self.selected_cheats.items():
            config['Cheats'][option_name] = option_var.get()
        with open(config_file, 'w', encoding="utf-8") as file:
            config["Manager"] = {}
            config["Manager"]["Cheat_Version"] = self.cheat_version.get()
            config.write(file)
        return

    # This is only required for the UI and FP mods.
    if not config.has_section("Options"):
        config["Options"] = {}
    config['Options']['UI'] = self.ui_var.get()
    config['Options']['First Person'] = self.fp_var.get()

    # Save the enable/disable choices
    for option_name, option_var in self.selected_options.items():
        config['Options'][option_name] = option_var.get()

    # Save the yuzu.exe path if provided
    if not config.has_section("Paths"):
        config["Paths"] = {}
    if self.mode == "Yuzu":
        if yuzu_path:
            config['Paths']['YuzuPath'] = yuzu_path
    if self.mode == "Ryujinx":
        if yuzu_path:
            config['Paths']['RyujinxPath'] = yuzu_path

    # Save the manager selected mode I.E Ryujinx/Yuzu
    config["Mode"] = {"ManagerMode": self.mode}

    if not config.has_section("Beyond"):
        config["Beyond"] = {}

    # UltraCam Beyond new patches.
    patch_info = self.ultracam_beyond.get("Keys", [""])
    for patch in self.BEYOND_Patches:
        patch_dict = patch_info[patch]
        patch_class = patch_dict["Class"]
        if patch_class.lower() == "dropdown":
            patch_Names = patch_dict["Name_Values"]
            index = patch_Names.index(self.BEYOND_Patches[patch].get())
            config["Beyond"][patch] = str(index)
            continue
        config["Beyond"][patch] = self.BEYOND_Patches[patch].get()

    log.info("User choices saved in Memory,"
             "Attempting to write into file.")
    # Write the updated configuration back to the file
    with open(config_file, 'w', encoding="utf-8") as file:
        config.write(file)
    log.info("Successfully written into log file")

def load_user_choices(self, config_file, mode=None):
    config = configparser.ConfigParser()
    config.read(config_file, encoding="utf-8")
    if mode == "Cheats":
        self.cheat_version.set(config.get("Manager", "Cheat_Version", fallback="Version - 1.2.1"))
        try:
            for option_name, option_var in self.selected_cheats.items():
                option_value = config.get('Cheats', option_name, fallback="Off")
                option_var.set(option_value)
        except AttributeError as e:
            # continue, not important.
            handle = e
        return

    # Load Ui and FP
    self.ui_var.set(config.get('Options', 'UI', fallback="None"))
    self.fp_var.set(config.get('Options', 'First Person', fallback="Off"))

    # Load UltraCam Beyond new patches.
    patch_info = self.ultracam_beyond.get("Keys", [""])
    for patch in self.BEYOND_Patches:
        patch_dict = patch_info[patch]
        patch_class = patch_dict["Class"]
        if patch_class.lower() == "dropdown":
            patch_Names = patch_dict["Name_Values"]
            try:
                self.BEYOND_Patches[patch].set(patch_Names[int(config["Beyond"][patch])])
            except KeyError:
                pass
            continue
        if patch_class.lower() == "scale":
            # use name for tag accuracy
            self.maincanvas.itemconfig(patch_dict["Name"], text=self.BEYOND_Patches[patch].get())
        try:
            self.BEYOND_Patches[patch].set(config["Beyond"][patch])
        except KeyError:
            pass

    # Load the enable/disable choices
    for option_name, option_var in self.selected_options.items():
        option_value = config.get('Options', option_name, fallback="Off")
        option_var.set(option_value)

    # Load the enable/disabled cheats
    try:
        for option_name, option_var in self.selected_cheats.items():
            option_value = config.get('Cheats', option_name, fallback="Off")
            option_var.set(option_value)
    except AttributeError as e:
        # continue, not important.
        handle = e

def apply_selected_preset(self, event=None):
    try:
        selected_preset = self.selected_preset.get()
    except AttributeError as e:
        selected_preset = "Saved"
        log.error(f"Failed to apply selected preset: {e}")

    if selected_preset.lower() == "saved":
        load_user_choices(self, self.config)
    elif selected_preset in self.presets:
        preset_to_apply = self.presets[selected_preset]
        for key, value in preset_to_apply.items():
            if value is True:
                preset_to_apply[key] = "On"
            elif value is False:
                preset_to_apply[key] = "Off"
            elif not isinstance(value, int) and not isinstance(value, float) and value.lower() in ["enable", "enabled", "on"]:
                preset_to_apply[key] = "On"
            elif not isinstance(value, int) and not isinstance(value, float) and value.lower() in ["disable", "disabled", "off"]:
                preset_to_apply[key] = "Off"
        # Apply the selected preset from the online presets
        self.apply_preset(self.presets[selected_preset])

def write_yuzu_config(self, configfile, title_id, section, setting, selection):
    if self.is_extracting is True:
        return
    os.makedirs(configfile, exist_ok=True)
    Custom_Config = os.path.join(configfile, f"{title_id}.ini")
    yuzuconfig = configparser.ConfigParser()
    yuzuconfig.read(Custom_Config, encoding="utf-8")
    if not yuzuconfig.has_section(section):
        yuzuconfig[f"{section}"] = {}
    yuzuconfig[f"{section}"][f"{setting}\\use_global"] = "false"
    yuzuconfig[f"{section}"][f"{setting}\\default"] = "false"
    yuzuconfig[f"{section}"][f"{setting}"] = selection
    with open(Custom_Config, "w", encoding="utf-8") as configfile:
        yuzuconfig.write(configfile, space_around_delimiters=False)

def write_ryujinx_config(self, configfile, setting, selection):
    if self.is_extracting is True:
        return

    with open(configfile, "r", encoding="utf-8") as file:
        data = json.load(file)
        data[setting] = selection

    os.remove(configfile)
    with open(configfile, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2)
