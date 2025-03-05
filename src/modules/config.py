from configuration.settings import *
import os, json

# fmt: off
def apply_preset(Manager, preset_options):
    # Manager.fetch_var(Manager.ui_var, preset_options, "UI")
    # Manager.fetch_var(Manager.fp_var, preset_options, "First Person")
    # Manager.fetch_var(Manager.selected_settings, preset_options, "Settings") # set Legacy settings.

    patch_info = Manager.ultracam_beyond.get("Keys", [""])

    for option_key, option_value in preset_options.items():
        if option_key in Manager.selected_options:
            Manager.selected_options[option_key].set(option_value)
        else:
            continue

    selected_preset = Manager.selected_preset.get()

    if selected_preset.lower() == "default":
        for option_key in Manager.UserChoices:
            patch_dict = patch_info[option_key.lower()]
            patch_class = patch_dict["Class"]
            patch_default = patch_dict["Default"]

            if patch_class == "dropdown":
                patch_names = patch_dict["Name_Values"]
                Manager.UserChoices[option_key.lower()].set(patch_names[patch_default])
            elif patch_class == "scale":
                Manager.maincanvas.itemconfig(patch_dict["Name"], text=patch_default)
                Manager.UserChoices[option_key.lower()].set(patch_default)
            else:
                if patch_class == "bool":
                    if patch_default is True: patch_default = "On"
                    if patch_default is False: patch_default = "Off"
                Manager.UserChoices[option_key.lower()].set(patch_default)

    for option_key, option_value in preset_options.items():
        if option_key.lower() in Manager.UserChoices:
            patch_dict = patch_info[option_key.lower()]
            patch_class = patch_dict["Class"]
            patch_default = patch_dict["Default"]

            if patch_class == "dropdown":
                patch_Names = patch_dict["Name_Values"]
                Manager.UserChoices[option_key.lower()].set(patch_Names[int(option_value)])
            elif patch_class == "scale":
                Manager.maincanvas.itemconfig(patch_dict["Name"], text=option_value)
                Manager.UserChoices[option_key.lower()].set(option_value)
            else:
                if patch_class == "bool":
                    if option_value is True: option_value = "On"
                    if option_value is False: option_value = "Off"
                Manager.UserChoices[option_key.lower()].set(option_value)
        else:
            continue

def setGameConfig(Manager, config):
    # UltraCam Beyond new patches.
    patch_info = Manager.ultracam_beyond.get("Keys", [""])
    sectionName = Manager._patchInfo.ID

    if not config.has_section(sectionName):
        config.add_section(sectionName)

    for patch in Manager.UserChoices:
        patch_dict = patch_info[patch]
        patch_class = patch_dict["Class"]

        if Manager.UserChoices[patch] == "auto":
            config.set(sectionName, patch, str(patch_dict["Default"]))
            continue
        elif Manager.UserChoices[patch].get() == "auto":
            config.set(sectionName, patch, str(patch_dict["Default"]))
            continue

        if patch_class.lower() == "dropdown":
            patch_Names = patch_dict["Name_Values"]
            index = patch_Names.index(Manager.UserChoices[patch].get())
            config.set(sectionName, patch, str(index))
            continue

        config.set(sectionName, patch, Manager.UserChoices[patch].get())

def loadGameConfig(Manager, config):
    # Load UltraCam Beyond new patches.
    patch_info = Manager.ultracam_beyond.get("Keys", [""])
    GameID = Manager._patchInfo.ID

    if not config.has_section(GameID):
        return

    for patch in Manager.UserChoices:
        patch_dict = patch_info[patch]
        patch_class = patch_dict["Class"]
        patch_default = patch_dict["Default"]
        if patch_class.lower() == "dropdown":
            patch_Names = patch_dict["Name_Values"]
            try:
                PatchIndex = int(config.get(GameID, patch))
                Manager.UserChoices[patch].set(patch_Names[PatchIndex])
            except KeyError:
                pass
            except ValueError:
                if config[Manager._patchInfo.ID][patch] == "auto":
                    PatchIndex = int(patch_default)
                    Manager.UserChoices[patch].set(patch_Names[PatchIndex])
                    continue
            continue
        if patch_class.lower() == "scale":
            # use name for tag accuracy
            Manager.maincanvas.itemconfig(patch_dict["Name"], text=Manager.UserChoices[patch].get())
        try:
            patch_type = patch_dict["Type"]

            if patch_type == "f32":
                Manager.UserChoices[patch].set(float(config.get(GameID, patch)))
            else:
                Manager.UserChoices[patch].set(config.get(GameID, patch))
        except (configparser.NoOptionError, KeyError):
            pass
        try:
            if patch_class.lower() == "bool":
                Manager.UserChoices[patch].set(config.get(GameID, patch))
        except (configparser.NoOptionError, KeyError):
            pass

def save_user_choices(Manager, config_file, Legacy_path=None):
    log.info(f"Saving user choices in {localconfig}")
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)

    # This is only required for the UI and FP mods.
    if not config.has_section("Options"):
        config["Options"] = {}
    # config['Options']['UI'] = Manager.ui_var.get()
    # config['Options']['First Person'] = Manager.fp_var.get()

    setGameConfig(Manager, config)

    # Save the enable/disable choices
    for option_name, option_var in Manager.selected_options.items():
        config['Options'][option_name] = option_var.get()

    # Save the Legacy.exe path if provided
    if not config.has_section("Paths"):
        config["Paths"] = {}
    if Manager.mode == "Legacy":
        if Legacy_path:
            config['Paths']['LegacyPath'] = Legacy_path
    if Manager.mode == "Ryujinx":
        if Legacy_path:
            config['Paths']['RyujinxPath'] = Legacy_path

    # Save the manager selected mode I.E Ryujinx/Legacy
    config["Mode"] = {"ManagerMode": Manager.mode}

    log.info("User choices saved in Memory,"
             "Attempting to write into file.")
    # Write the updated configuration back to the file
    with open(config_file, 'w', encoding="utf-8") as file:
        config.write(file)
    log.info("Successfully written into log file")

def load_user_choices(Manager, config_file, mode=None):
    config = configparser.ConfigParser()
    config.read(config_file, encoding="utf-8")

    loadGameConfig(Manager, config)

    # Load the enable/disable choices
    for option_name, option_var in Manager.selected_options.items():
        option_value = config.get('Options', option_name, fallback="Off")
        option_var.set(option_value)

def apply_selected_preset(manager, event=None):
    from modules.FrontEnd.FrontEnd import Manager
    manager: Manager = manager

    try:
        selected_preset = manager.selected_preset.get()
    except AttributeError as e:
        selected_preset = "Saved"
        log.error(f"Failed to apply selected preset: {e}")

    presets = manager._patchInfo.LoadPresetsJson()

    if selected_preset.lower() == "saved":
        load_user_choices(manager, manager.config)
    elif selected_preset in presets:
        preset_to_apply = presets[selected_preset]
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
        apply_preset(manager, presets[selected_preset])

def write_Legacy_config(Manager, config_file, title_id, section, setting, selection):
    os.makedirs(config_file, exist_ok=True)
    Custom_Config = os.path.join(config_file, f"{title_id}.ini")
    Legacyconfig = configparser.ConfigParser()
    Legacyconfig.read(Custom_Config, encoding="utf-8")
    if not Legacyconfig.has_section(section):
        Legacyconfig[f"{section}"] = {}
    Legacyconfig[f"{section}"][f"{setting}\\use_global"] = "false"
    Legacyconfig[f"{section}"][f"{setting}\\default"] = "false"
    Legacyconfig[f"{section}"][f"{setting}"] = selection
    with open(Custom_Config, "w", encoding="utf-8") as config_file:
        Legacyconfig.write(config_file, space_around_delimiters=False)

def write_ryujinx_config(Manager, config_file, setting, selection):

    if not os.path.exists(config_file):
        log.error(f"RYUJINX CONFIG DOESN'T EXIST! {config_file}")
        return

    with open(config_file, "r", encoding="utf-8") as file:
        data = json.load(file)
        data[setting] = selection

    os.remove(config_file)
    with open(config_file, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=2)

def load_config_game(Manager, config_file):
    ''' Loads the current selected Configuration game. '''
    config = configparser.ConfigParser()
    config.read(config_file, encoding="utf-8")
    if not config.has_section("Options"):
        config["Options"] = {}
        return "0"
    
    return config.get("Options", "Game", fallback=Manager._patchInfo.ID)

def save_config_game(Manager, config_file):
    ''' Saves the current selected Configuration game. '''
    config = configparser.ConfigParser()
    config.read(config_file, encoding="utf-8")
    if not config.has_section("Options"):
        config["Options"] = {}
    config.set("Options", "Game", Manager._patchInfo.ID)

    with open(config_file, 'w', encoding="utf-8") as file:
        config.write(file)
