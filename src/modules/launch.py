import os.path
import subprocess
from configuration.settings import *

def is_process_running(process_name):
    cmd = 'tasklist /fi "imagename eq {}"'.format(process_name)
    output = subprocess.check_output(cmd, shell=True).decode()
    if process_name.lower() in output.lower():
        return True
    else:
        return False

def launch_GAME(self):
    config = configparser.ConfigParser()
    config.read(localconfig)
    Game_PATH = config.get("Paths", "game_path", fallback="None")
    log.info(f"Launching game {Game_PATH}")

    if not os.path.exists(Game_PATH):
        return log.warning(f"Game not found in {Game_PATH}")

    if self.mode == "Yuzu":
        mode = "yuzu.exe"
        if is_process_running("yuzu.exe"):
            log.info("Yuzu is already running in the background.")
            return

        yuzupath = self.load_yuzu_path(localconfig).split("yuzu.exe")[0]
        if os.path.exists(yuzupath):
            Yuzu_PATH = yuzupath.split("/yuzu.exe")[0]
        else:
            Yuzu_PATH = os.path.join(os.path.expanduser("~"), "Appdata", "Local", "yuzu", "yuzu-windows-msvc")

        os.chdir(Yuzu_PATH)


    if self.mode == "Ryujinx":
        mode = "Ryujinx.exe"

    cmd = [f'{mode}', '-u', '1', '-f', '-g', f'{Game_PATH}']
    process = subprocess.Popen(cmd, shell=False)