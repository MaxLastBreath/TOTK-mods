import logging, sys, platform, psutil, os, colorlog
from modules.macos import macos_path
from modules.scaling import *
import modules.hwinfo as hwinfo


def start_logger(file="logger.log", Name=None, formatter=None):

    filename = file

    # Set custom path for MacOS to avoid crash
    if platform.system() == "Darwin":
        if not os.path.exists(macos_path):
            os.makedirs(macos_path)
        filename = os.path.join(macos_path, filename)

    new_logger = logging.getLogger(Name)
    new_logger.setLevel(logging.INFO)

    new_logger.propagate = False

    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(
        logging.Formatter(
            "TIME: %(asctime)s,%(msecs)d - %(name)s - %(levelname)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )

    # Add handlers to the logger
    new_logger.addHandler(file_handler)
    new_logger.addHandler(console_handler)

    return new_logger


formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s : %(levelname)s : %(message)s",
    datefmt="%H:%M:%S",
    log_colors={
        "DEBUG": "green",
        "INFO": "purple",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# logger 1
log = start_logger("logger.log", None, formatter)

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s : %(levelname)s : %(message)s",
    datefmt="%H:%M:%S",
    log_colors={
        "DEBUG": "yellow",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# logger 2 for green color text.
superlog = start_logger("superlog.log", "Logger", formatter)

CPU, FREQUENCY = hwinfo.get_cpu_info(log)
gpu_name = hwinfo.get_gpu_name(log)

# Print Memory
try:
    memory_info = psutil.virtual_memory()
    total_memory = round(memory_info.total / (1024 * 1024 * 1024))
    memory_used = memory_info.percent
except Exception as e:
    log.warning(
        f"The System Memory was not detected, nothing to be concerned about. {e}"
    )
    total_memory = "Undetected"

superlog.info(
    f"\n\n\n\nAttempting to start Application.\n"
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
