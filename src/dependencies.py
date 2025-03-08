import subprocess
import platform

command = [
    "pip", 
    "install", 
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
    "https://github.com/MaxLastBreath/ttkbootstrapFIX/zipball/master"
]

if platform.system() == "Windows":
    command.append("wmi")

# Execute the pip install command
subprocess.run(command)