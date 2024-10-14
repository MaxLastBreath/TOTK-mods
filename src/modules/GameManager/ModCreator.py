from modules.logger import log, superlog
from modules.config import *
import re, os

class ResolutionVector:
    w = 16
    h = 9
    s = 1024

    def __init__(self, x, y):
        self.w = float(x)
        self.h = float(y)

    def addShadows(self, shadows):
        self.s = float(shadows)

    def getShadowScale(self):
        return self.s / 1024

    def getscale(self):
        return self.w * self.h / 16 * 9
    
    def getFullScale(self):
        if (self.getShadowScale() > self.getscale()):
            return self.getShadowScale
        else :
            return self.getscale()


class ModCreator:

    @classmethod
    def CreateCheats(cls, filemgr):
        """
        This function creates a cheat manager patcher, primarily used only for TOTK right now.
        """
        superlog.info("Starting Cheat patcher.")
        save_user_choices(filemgr, filemgr.config, None, "Cheats")
        selected_cheats = {}
        for option_name, option_var in filemgr._manager.selected_cheats.items():
            selected_cheats[option_name] = option_var.get()
        # Logic for Updating Visual Improvements/Patch Manager Mod. This new code ensures the mod works for Ryujinx and Legacy together.
        for version_option in filemgr._manager.cheat_options:
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
        filemgr._manager.remove_list.append("Cheat Manager Patch")
        superlog.info("Applied cheats successfully.")

    @classmethod
    # This no longer works, it's currently disabled and unused, the logic may be refractored in the future.
    def CreateExefs(cls, patchinfo, directory, version_options, selected_options):
        """
        creates an EXEFs patch for the respective game.
        """
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
        """
        This function configues the mod's config file (.ini) dynamically based on games.
        Requires manager, which then fetches UserChoices from manager to read all the different parameters.

        Parameters:
        manager (FrontEnd): The frontend UI manager.
        config (configparser): The config file parser.
        """
        
        patch_info = manager.ultracam_beyond.get("Keys", [""])

        for patch in manager.UserChoices:
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
            if manager.UserChoices[patch] == "auto" or manager.UserChoices[patch].get() == "auto":
                if patch_class.lower() == "dropdown":
                    patch_Names = patch_dict["Values"]
                    config[patch_Config[0]][patch_Config[1]] = str(patch_Names[patch_Default])
                else:
                    config[patch_Config[0]][patch_Config[1]] = str(patch_Default)
                continue

            if patch_class.lower() == "bool" or patch_class.lower() == "scale":
                config[patch_Config[0]][patch_Config[1]] = manager.UserChoices[patch].get()

            if patch_class.lower() == "dropdown":
                # exclusive to dropdown.
                patch_Names = patch_dict["Name_Values"]
                patch_Values = patch_dict["Values"]
                index = patch_Names.index(manager.UserChoices[patch].get())
                config[patch_Config[0]][patch_Config[1]] = str(patch_Values[index])

    @classmethod
    def UCAspectRatioPatcher(cls, manager, config):
        patch_info = manager.ultracam_beyond.get("Keys", [""])
        
        if "aspect" not in patch_info:
            return
        
        ARIndex = patch_info["aspect"]["Name_Values"].index(manager.UserChoices["aspect"].get())
        AspectList = patch_info["aspect"]["Values"][ARIndex]
        AspectRatio = ResolutionVector(AspectList[0], AspectList[1])

        Section = patch_info["aspect"]["Config_Class"][0]
        Width = patch_info["aspect"]["Config_Class"][1]
        Height = patch_info["aspect"]["Config_Class"][2]

        config[Section][Width]  = str(AspectRatio.w)
        config[Section][Height] = str(AspectRatio.h)
        

    @classmethod
    def UCResolutionPatcher(cls, filemgr, manager, config):
        """
        This function configues the mod's config file (.ini) dynamically based on games.
        This function requires the file manager in order to read the locations of Ryujinx config file and Legacy config file respectively.
        This function also uses the UI manager to read the state of our UI, if we are using "Legacy" or Ryujinx modes respectively.
        Requires manager, which then fetches UserChoices from manager to read the resolution, shadows and aspect ratios parameters.
        
        Parameters:
        filemgr (FileManager): the file manager is required here.
        manager (FrontEnd): The frontend UI manager.
        config (configparser): The config file parser.
        """

        patch_info = manager.ultracam_beyond.get("Keys", [""])

        try: 
            resolution = manager.UserChoices["resolution"].get()
        except Exception as e :
            resolution = 1

        if "resolution" not in patch_info:
            return
        
        if "shadows" in patch_info:
            shadows = int(manager.UserChoices["shadow resolution"].get().split("x")[0])
        else:
            shadows = 1024

        ResInfo = patch_info["resolution"]["Values"][patch_info["resolution"]["Name_Values"].index(resolution)].split("x")
        
        Resolution = ResolutionVector(ResInfo[0], ResInfo[1])
        Resolution.addShadows(shadows)

        layout = 0
        if  (Resolution.getFullScale() < 0):
            layout = 0
        elif(Resolution.getFullScale() > 1):
            layout = 1
        elif(Resolution.getFullScale() > 5):
            layout = 2

        if manager.mode == "Legacy":
            write_Legacy_config(manager, filemgr.TOTKconfig, manager._patchInfo.ID, "Renderer", "resolution_setup", "2")
            write_Legacy_config(manager, filemgr.TOTKconfig, manager._patchInfo.ID, "Core", "memory_layout_mode", str(layout))
            write_Legacy_config(manager, filemgr.TOTKconfig, manager._patchInfo.ID, "System", "use_docked_mode", "true")

            if layout > 0:
                write_Legacy_config(manager, filemgr.TOTKconfig, manager._patchInfo.ID, "Renderer", "vram_usage_mode", "1")
            else:
                write_Legacy_config(manager, filemgr.TOTKconfig, manager._patchInfo.ID, "Renderer", "vram_usage_mode", "0")

        if manager.mode == "Ryujinx":
            write_ryujinx_config(manager, filemgr.ryujinx_config, "res_scale", 1)
            if (layout > 0):
                write_ryujinx_config(manager, filemgr.ryujinx_config, "expand_ram", True)
            else:
                write_ryujinx_config(manager, filemgr.ryujinx_config, "expand_ram", False)

        Section =   patch_info["resolution"]["Config_Class"][0]
        Width   =   patch_info["resolution"]["Config_Class"][1]
        Height  =   patch_info["resolution"]["Config_Class"][2]

        config[Section][Width]  = str(int(Resolution.w))
        config[Section][Height] = str(int(Resolution.h))