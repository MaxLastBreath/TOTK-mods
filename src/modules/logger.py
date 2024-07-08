import logging
import sys
import platform
import psutil
import GPUtil
import os
from modules.scaling import *
from modules.macos import macos_path
import subprocess
import modules.hwinfo as hwinfo

def start_logger():
    filename = "logger.txt"

    # Set custom path for MacOS to avoid crash
    if platform.system() == "Darwin":
        if not os.path.exists(macos_path):
            os.makedirs(macos_path)
        filename = os.path.join(macos_path, filename)

    logging.basicConfig(filename=filename,
                        filemode='a',
                        format='TIME: %(asctime)s,%(msecs)d - %(name)s - %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
    new_logger = logging.getLogger('LOGGER')
    logging.getLogger('LOGGER').addHandler(logging.StreamHandler(sys.stdout))
    return new_logger

log = start_logger()

CPU, FREQUENCY = hwinfo.get_cpu_info()
gpu_name = hwinfo.get_gpu_name()

# Print Memory
try:
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total//1048576000
    memory_used = memory_info.percent
except Exception as e:
    log.warning(f"The System Memory was not detected, nothing to be concerned about. {e}")
    total_memory = "Undetected"

log.info(f"\n\n\n\nAttempting to start Application.\n"
         f"__SystemINFO__\n"
         f"System: {platform.system()}\n"
         f"GPU: {gpu_name}\n"
         f"RAM: {total_memory} GB {FREQUENCY} MHz and used {memory_used}%\n"
         f"CPU: {CPU}"
         f"\n"
         )


def write_data(file_name, data, mode, space=None):
    try:
        with open(file_name, mode, encoding="utf-8") as file:
            file.write(data, space_around_delimiters=False)
        logging.info(f"Successfully wrote %d bytes into %s", len(data), file_name)
    except FileNotFoundError:
        logging.exception(f"Failed to write data into %s", file_name)