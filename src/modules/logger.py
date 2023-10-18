import logging
import sys
import platform
import psutil
import GPUtil
from modules.scaling import *


def start_logger():
    logging.basicConfig(filename="logger.txt",
                        filemode='a',
                        format='TIME: %(asctime)s,%(msecs)d - %(name)s - %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)
    new_logger = logging.getLogger('LOGGER')
    logging.getLogger('LOGGER').addHandler(logging.StreamHandler(sys.stdout))
    return new_logger
log = start_logger()

try:
    gpus = GPUtil.getGPUs()
    gpu_name = gpus[0].name
except Exception as e:
    log.warning(f"The GPU was not detected, nothing to be concerned about. {e}")
    gpu_name = "Undetected"

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
         f"RAM: {total_memory} GB and used {memory_used}%\n"
         f"\n"
         )


def write_data(file_name, data, mode, space=None):
    try:
        with open(file_name, mode) as file:
            file.write(data, space_around_delimiters=False)
        logging.info(f"Successfully wrote %d bytes into %s", len(data), file_name)
    except FileNotFoundError:
        logging.exception(f"Failed to write data into %s", file_name)