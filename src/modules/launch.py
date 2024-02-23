import os.path
import subprocess
from tkinter import filedialog, Toplevel
from configuration.settings import *

def is_process_running(process_name):
    try:
        cmd = 'tasklist /fi "imagename eq {}"'.format(process_name)
        output = subprocess.check_output(cmd, shell=True).decode()
        if process_name.lower() in output.lower():
            return True
        else:
            return False
    except Exception as e:
        log.info(f"Couldn`t detect if {process_name} is running.")

def select_game_file(command=None):
    # Open a file dialog to browse and select yuzu.exe
    game_path = filedialog.askopenfilename(
        title=f"Please select Tears of The Kingdom Game File.",
        filetypes=[("Nintendo Gamefile", ["*.nsp", "*.xci", "*.NSP", "*.XCI"]), ("All Files", "*.*")]
    )
    if game_path:
        config = configparser.ConfigParser()
        config.read(localconfig, encoding="utf-8")

        if not config.has_section("Paths"):
            config.add_section("Paths")
        config.set("Paths", "game_path", game_path)
    else:
        return
    with open(localconfig, "w", encoding="utf-8") as configfile:
        config.write(configfile, space_around_delimiters=False)
    return game_path

def launch_GAME(self):
    config = configparser.ConfigParser()
    config.read(localconfig, encoding="utf-8")
    Game_PATH = config.get("Paths", "game_path", fallback="None")

    if not os.path.exists(Game_PATH):
        log.warning(f"Game not found in {Game_PATH}\n Please select your game file.")
        Game_PATH = select_game_file()

    log.info(f"Launching game {Game_PATH}")

    if self.mode == "Yuzu":
        mode = "yuzu.exe"
        if is_process_running("yuzu.exe"):
            log.info("Yuzu is already running in the background.")
            return

        yuzupath = self.load_yuzu_path(localconfig)
        if os.path.exists(yuzupath):
            Yuzu_PATH = yuzupath.split("/yuzu.exe")[0]
        else:
            Yuzu_PATH = os.path.join(os.path.expanduser("~"), "Appdata", "Local", "yuzu", "yuzu-windows-msvc")

        os.chdir(Yuzu_PATH)
        cmd = [f'{mode}', '-u', '1', '-f', '-g', f'{Game_PATH}']

    if self.mode == "Ryujinx":
        mode = "Ryujinx.exe"

        if is_process_running("Ryujinx.exe"):
            log.info("Ryujinx is already running in the background.")
            return

        ryujinx_path = self.load_yuzu_path(localconfig)
        if os.path.exists(ryujinx_path):
            Ryujinx_PATH = ryujinx_path.split("/Ryujinx.exe")[0]
            Ryujinx_PATH = Ryujinx_PATH.split("/RyujinxAva.exe")[0]
        else:
            Ryujinx_PATH = self.select_yuzu_exe()
            if Ryujinx_PATH is None: return
            else: Ryujinx_PATH = Ryujinx_PATH.split("/Ryujinx.exe")[0]

        os.chdir(Ryujinx_PATH)
        cmd = [f'{mode}', '-f', f'{Game_PATH}']

    process = subprocess.Popen(cmd, shell=False)