import subprocess, platform

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
    command += "wmi"

subprocess.run(" ".join(command), shell=True)