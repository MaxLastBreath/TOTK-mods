from modules.logger import log
from modules.config import *
import re, os

class ModCreator:

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
