import os
import platform
import subprocess

def compile_to_exe(script_name):
    platform_name = platform.system()

    if platform_name == "Windows":
        add_data_option = "HUD/*:HUD"
        pyinstaller_cmd = f"pyinstaller {script_name} --onefile --noconsole --add-data \"{add_data_option}\""
    else:
        add_data_option = "HUD/*:HUD"
        pyinstaller_cmd = f"pyinstaller {script_name} --onefile --add-data \"HUD/*:HUD\""

    subprocess.run(pyinstaller_cmd, shell=True)

if __name__ == "__main__":
    script_to_compile = "run.py" 

    compile_to_exe(script_to_compile)
