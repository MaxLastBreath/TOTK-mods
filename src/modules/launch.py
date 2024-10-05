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