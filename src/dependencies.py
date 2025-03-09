import subprocess
import platform

command = [
    "python", "-m", "pip", "install",
    "requests",
    "patool",
    "screeninfo",
    "packaging",
    "GPUtil",
    "colorlog",
    "psutil",
    "pyperclip",
    "pyinstaller",
    "nuitka",
    "numpy",
    "zstandard",
    "imageio",
    "https://github.com/MaxLastBreath/ttkbootstrapFIX/zipball/master"
]

if platform.system() == "Windows":
    command.append("wmi")

subprocess.run(command)