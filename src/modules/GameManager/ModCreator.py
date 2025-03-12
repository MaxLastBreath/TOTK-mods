from modules.FrontEnd.FrontEndMode import NxMode
from modules.logger import log, superlog
from modules.config import *
import re, os


class ResolutionVector:
    w: float | int = 16
    h: float | int = 9
    s: int = 1024

    def __init__(self, width, height):
        """Initialize the class with Width and Height of the desired Resolution."""

        self.w = float(width)
        self.h = float(height)

    def addShadows(self, shadows):
        """Add Shadow Resolution if game supports it."""

        self.s = float(shadows)

    def getShadowScale(self):
        """Get the amount of shadow increased in float."""

        return float(self.s / 1024)

    def getscale(self):
        """Get the Total Increase of resolution in float."""

        scale = float(self.w * self.h) / float(1920 * 1080)
        return scale

    def getFullScale(self):
        """Get the the higher scale between Resolution and Shadow Resolution."""

        if self.getShadowScale() > self.getscale():
            return self.getShadowScale()
        else:
            return self.getscale()

    def getRamLayout(self):
        """Get the Estimated Ram Layout."""

        layout = 0
        if self.getFullScale() < 0:
            layout = 0
        if self.getFullScale() > 1:
            layout = 1
        if self.getFullScale() > 5:
            layout = 2
        return layout


class ModCreator:

    @classmethod
    def CreateCheats(cls):
        """This function creates a cheat manager patcher, primarily used only for TOTK right now."""

        from modules.GameManager.CheatManager import Cheats

        Cheats.CreateCheats()

    @classmethod
    # This no longer works, it's currently disabled and unused, the logic may be refractored in the future.
    def CreateExefs(cls, patchinfo, directory, version_options, selected_options):
        """creates an EXEFs patch for the respective game."""

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
                    if key not in ["Source", "nsobid", "offset", "version", "Version"] and not selected_options[key].get() == "Off":  # fmt: skip
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
            # fmt: off
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
    def UCRyujinxRamPatcher(cls, manager, filemgr, layout):
        """Patches Ryujinx specific Settings, such as RAM from 4 or 8GB."""
        
        if not os.path.exists(filemgr._emuconfig):
            log.error(f"Ryujinx config doesn't exist {filemgr._emuconfig} Please Run Ryujinx or press Browse to direct the app to Ryujinx.exe")
            return

        if (read_ryujinx_version(filemgr._emuconfig) >= 54):
            # GreemDev Ryujinx
            write_ryujinx_config(filemgr, filemgr._emuconfig,  "dram_size", layout)
            log.warning(f"Expanding Ram Size to Type {layout}")
        else:
            # Original Ryujinx
            if layout > 0:
                log.warning(f"Expanding Ryujinx RAM mode to 8GB, {layout}")
                write_ryujinx_config(filemgr, filemgr._emuconfig,  "expand_ram", True)
            else:
                log.warning(f"Reverting Ryujinx RAM mode to 4GB, {layout}")
                write_ryujinx_config(filemgr, filemgr._emuconfig,  "expand_ram", False)

    @classmethod
    def UCLegacyRamPatcher(cls, manager, filemgr, layout):
        """Patches bunch of settings in Legacy Emulators, VRAM, RAM etc. Based on Resolution and shadow resolution outputs mostly."""

        write_Legacy_config(manager, filemgr._gameconfig, manager._patchInfo.ID, "Core", "memory_layout_mode", str(layout))  # fmt: skip
        write_Legacy_config(manager, filemgr._gameconfig, manager._patchInfo.ID, "System", "use_docked_mode", "true")  # fmt: skip

        if layout > 0:
            write_Legacy_config(manager, filemgr._gameconfig, manager._patchInfo.ID, "Renderer", "vram_usage_mode", "1")  # fmt: skip
        else:
            write_Legacy_config(manager, filemgr._gameconfig, manager._patchInfo.ID, "Renderer", "vram_usage_mode", "0")  # fmt: skip

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
        except Exception:
            resolution = 1

        if "shadows" in patch_info:
            shadows = int(manager.UserChoices["shadow resolution"].get().split("x")[0])
        else:
            shadows = 1024

        ResInfo = patch_info["resolution"]["Values"][
            patch_info["resolution"]["Name_Values"].index(resolution)
        ].split("x")

        Resolution = ResolutionVector(ResInfo[0], ResInfo[1])
        Resolution.addShadows(shadows)

        if NxMode.isLegacy():
            # for emulator scale
            new_scale = 1
            if (manager._patchInfo.ResolutionScale):
                new_scale += int(manager._EmulatorScale.get())

            write_Legacy_config(manager, filemgr._gameconfig, manager._patchInfo.ID, "Renderer", "resolution_setup", f"{new_scale}")  # fmt: skip
            cls.UCLegacyRamPatcher(manager, filemgr, Resolution.getRamLayout())

        if NxMode.isRyujinx():
            new_scale = 1
            if (manager._patchInfo.ResolutionScale):
                new_scale = int(manager._EmulatorScale.get())

            write_ryujinx_config(filemgr, filemgr._emuconfig, "res_scale", new_scale)  # fmt: skip
            cls.UCRyujinxRamPatcher(manager, filemgr, Resolution.getRamLayout())

        Section = patch_info["resolution"]["Config_Class"][0]
        Width = patch_info["resolution"]["Config_Class"][1]
        Height = patch_info["resolution"]["Config_Class"][2]

        config[Section][Width] = str(int(Resolution.w))
        config[Section][Height] = str(int(Resolution.h))

    @classmethod
    def UCAspectRatioPatcher(cls, manager, config):
        """
        Patches Aspect Ratios for specific games...

        Parameters:
        manager (Manager Class): The frontend UI manager.
        config (configparser): The config file parser.
        """

        patch_info = manager.ultracam_beyond.get("Keys", [""])

        if "aspect" not in patch_info:
            return

        ARIndex = patch_info["aspect"]["Name_Values"].index(
            manager.UserChoices["aspect"].get()
        )
        AspectList = patch_info["aspect"]["Values"][ARIndex]
        AspectRatio = ResolutionVector(AspectList[0], AspectList[1])

        Section = patch_info["aspect"]["Config_Class"][0]
        Width = patch_info["aspect"]["Config_Class"][1]
        Height = patch_info["aspect"]["Config_Class"][2]

        config[Section][Width] = str(AspectRatio.w)
        config[Section][Height] = str(AspectRatio.h)
