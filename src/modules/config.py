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
        with open(config_file, 'w') as file:
            config["Manager"] = {}
            config["Manager"]["Cheat_Version"] = self.cheat_version.get()
            config.write(file)
        return

    # Save the selected options
    if not config.has_section("Options"):
        config["Options"] = {}
    config['Options']['DFPS Version'] = self.DFPS_var.get()
    config['Options']['Resolution'] = self.resolution_var.get()
    config['Options']['Aspect Ratio'] = self.aspect_ratio_var.get()
    config['Options']['FPS'] = self.fps_var.get()
    config['Options']['ShadowResolution'] = self.shadow_resolution_var.get()
    config['Options']['UI'] = self.ui_var.get()
    config['Options']['First Person'] = self.fp_var.get()
    config['Options']['Fov'] = self.fov_var.get()

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
        self.cheat_version.set(config.get("Manager", "Cheat_Version", fallback="Version - 1.2.0"))
        try:
            for option_name, option_var in self.selected_cheats.items():
                option_value = config.get('Cheats', option_name, fallback="Off")
                option_var.set(option_value)
        except AttributeError as e:
            # continue, not important.
            handle = e
        return

    # Load the selected options
    if config.get('Options', 'DFPS Version', fallback="UltraCam") not in ["UltraCam", "DFPS Legacy"]:
        self.DFPS_var.set("UltraCam")
    else:
        self.DFPS_var.set(config.get('Options', 'DFPS Version', fallback="UltraCam"))

    self.cheat_version.set(config.get("Manager", "Cheat_Version", fallback="Version - 1.2.1"))
    self.resolution_var.set(config.get('Options', 'Resolution', fallback=self.dfps_options.get("ResolutionNames", [""])[2]))
    self.aspect_ratio_var.set(config.get('Options', 'Aspect Ratio', fallback=AR_list[0]))
    self.fps_var.set(config.get('Options', 'FPS', fallback=str(self.dfps_options.get("FPS", [])[2])))
    self.fps_var_new.set(config.get('Options', 'FPS', fallback=str(self.dfps_options.get("FPS", [])[2])))
    self.shadow_resolution_var.set(config.get('Options', 'ShadowResolution', fallback=self.dfps_options.get("ShadowResolutionNames", [""])[0])) # Shadow Auto
    self.shadow_resolution_var_new.set(config.get('Options', 'ShadowResolution',
                                              fallback=self.ultracam_options.get("ShadowResolutionNames", [""])[
                                                  0]))  # Shadow Auto
    self.fov_var.set(config.get('Options', 'Fov', fallback=50))  # FOV 50
    self.ui_var.set(config.get('Options', 'UI', fallback="None"))
    self.fp_var.set(config.get('Options', 'First Person', fallback="Off"))
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

def write_yuzu_config(configfile, section, setting, selection):
    yuzuconfig = configparser.ConfigParser()
    yuzuconfig.read(configfile, encoding="utf-8")
    if not yuzuconfig.has_section(section):
        yuzuconfig[f"{section}"] = {}
    yuzuconfig[f"{section}"][f"{setting}\\use_global"] = "false"
    yuzuconfig[f"{section}"][f"{setting}\\default"] = "false"
    yuzuconfig[f"{section}"][f"{setting}"] = selection
    with open(configfile, "w", encoding="utf-8") as configfile:
        yuzuconfig.write(configfile, space_around_delimiters=False)

def write_ryujinx_config(configfile, setting, selection):
    with open(configfile, "r", encoding="utf-8") as file:
        data = json.load(file)
        data[setting] = selection

    os.remove(configfile)
    with open(configfile, 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2)
