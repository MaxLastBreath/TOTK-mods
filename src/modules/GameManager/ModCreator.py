from modules.logger import log
from modules.config import *
import re, os

class ModCreator:

    def convert_resolution(width, height, ARR_width, ARR_height):
        original_aspect_ratio = width / height

        if ARR_width / ARR_height > original_aspect_ratio:
            # Horizontal aspect ratio
            new_width = int(height * (ARR_width / ARR_height))
            new_height = height
        else:
            # Vertical aspect ratio
            new_height = int(width * (ARR_height / ARR_width))
            new_width = width

        return new_width, new_height

    @classmethod
    def CreateCheats(cls, filemgr):
        log.info("Starting Cheat patcher.")
        save_user_choices(filemgr, filemgr.config, None, "Cheats")
        selected_cheats = {}
        for option_name, option_var in filemgr._frontend.selected_cheats.items():
            selected_cheats[option_name] = option_var.get()
        # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Legacy together.
        for version_option in filemgr._frontend.cheat_options:
            version = version_option.get("Version", "")
            mod_path = os.path.join(filemgr.load_dir, "Cheat Manager Patch", "cheats")

            # Create the directory if it doesn't exist
            os.makedirs(mod_path, exist_ok=True)

            filename = os.path.join(mod_path, f"{version}.txt")
            all_values = []
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    file.flush()
                    # file.write(version_option.get("Source", "") + "\n") - makes cheats not work
                    for key, value in version_option.items():
                        if key not in ["Source", "Aversion", "Version"] and selected_cheats[key] == "Off":
                            continue
                        if key in selected_cheats:
                                file.write(value + "\n")
            except Exception as e:
                log.error(f"ERROR! FAILED TO CREATE CHEAT PATCH. {e}")
        filemgr._frontend.remove_list.append("Cheat Manager Patch")
        log.info("Applied cheats successfully.")

    @classmethod
    # This no longer works, it's currently disabled and unused, the logic may be refractored in the future.
    def CreateExefs(cls, patchinfo, directory, version_options, selected_options):
        for version_option in version_options:
            version = version_option.get("version", "")
            mod_path = os.path.join(directory, patchinfo.ModName, "exefs")

            # Create the directory if it doesn't exist
            os.makedirs(mod_path, exist_ok=True)

            filename = os.path.join(mod_path, f"{version}.pchtxt")
            all_values = []
            with open(filename, "w", encoding="utf-8") as file:
                file.write(version_option.get("Source", "") + "\n")
                file.write(version_option.get("nsobid", "") + "\n")
                file.write(version_option.get("offset", "") + "\n")
                for key, value in version_option.items():
                    if key not in ["Source", "nsobid", "offset", "version", "Version"] and not selected_options[key].get() == "Off":
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

    @classmethod
    def UCAutoPatcher(cls, manager, config):
        patch_info = manager.ultracam_beyond.get("Keys", [""])

        for patch in manager.BEYOND_Patches:
            if patch.lower() in ["resolution", "aspect ratio"]:
                continue

            patch_dict = patch_info[patch]
            patch_class = patch_dict["Class"]
            patch_Config = patch_dict["Config_Class"]
            patch_Default = patch_dict["Default"]

            # Ensure we have the section required.
            if not config.has_section(patch_Config[0]):
                config[patch_Config[0]] = {}

            # In case we have an auto patch.
            if manager.BEYOND_Patches[patch] == "auto" or manager.BEYOND_Patches[patch].get() == "auto":
                if patch_class.lower() == "dropdown":
                    patch_Names = patch_dict["Values"]
                    config[patch_Config[0]][patch_Config[1]] = str(patch_Names[patch_Default])
                else:
                    config[patch_Config[0]][patch_Config[1]] = str(patch_Default)
                continue

            if patch_class.lower() == "bool" or patch_class.lower() == "scale":
                config[patch_Config[0]][patch_Config[1]] = manager.BEYOND_Patches[patch].get()

            if patch_class.lower() == "dropdown":
                # exclusive to dropdown.
                patch_Names = patch_dict["Name_Values"]
                patch_Values = patch_dict["Values"]
                index = patch_Names.index(manager.BEYOND_Patches[patch].get())
                config[patch_Config[0]][patch_Config[1]] = str(patch_Values[index])

    @classmethod
    def UCResolutionPatcher(cls, filemgr, manager, config):
        patch_info = manager.ultracam_beyond.get("Keys", [""])

        try: 
            resolution = manager.BEYOND_Patches["resolution"].get()
        except Exception as e :
            resolution = 1

        try:
            shadows = int(manager.BEYOND_Patches["shadow resolution"].get().split("x")[0])
        except Exception as e :
            shadows = 1024

        if "resolution" not in patch_info:
            return

        # ARR = manager.BEYOND_Patches["aspect ratio"].get().split("x")
        ARR = [16, 9]
        New_Resolution = patch_info["resolution"]["Values"][patch_info["resolution"]["Name_Values"].index(resolution)].split("x")
        New_Resolution = cls.convert_resolution(int(New_Resolution[0]), int(New_Resolution[1]), int(ARR[0]), int(ARR[1]))

        scale_1080 = 1920*1080
        scale_shadows = round(shadows / 1024)
        New_Resolution_scale = int(New_Resolution[0]) * int(New_Resolution[1])
        new_scale = New_Resolution_scale / scale_1080

        if (scale_shadows > new_scale):
            new_scale = scale_shadows
            log.info(f"scale:{new_scale}")

        layout = 0
        if(new_scale < 0):
            layout = 0
        if(new_scale > 1):
            layout = 1
        if(new_scale > 6):
            layout = 2

        if manager.mode == "Legacy":
            write_Legacy_config(manager, filemgr.TOTKconfig, manager.title_id, "Renderer", "resolution_setup", "2")
            write_Legacy_config(manager, filemgr.TOTKconfig, manager.title_id, "Core", "memory_layout_mode", f"{layout}")
            write_Legacy_config(manager, filemgr.TOTKconfig, manager.title_id, "System", "use_docked_mode", "true")

            if layout > 0:
                write_Legacy_config(manager, filemgr.TOTKconfig, manager.title_id, "Renderer", "vram_usage_mode", "1")
            else:
                write_Legacy_config(manager, filemgr.TOTKconfig, manager.title_id, "Renderer", "vram_usage_mode", "0")

        if manager.mode == "Ryujinx":
            write_ryujinx_config(manager, filemgr.ryujinx_config, "res_scale", 1)
            if (layout > 0):
                write_ryujinx_config(manager, filemgr.ryujinx_config, "expand_ram", True)
            else:
                write_ryujinx_config(manager, filemgr.ryujinx_config, "expand_ram", False)

        config["Resolution"]["Width"] = str(New_Resolution[0])
        config["Resolution"]["Height"] = str(New_Resolution[1])