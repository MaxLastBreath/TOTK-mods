import subprocess

command = [
    "pip", 
    "install", 
    "requests", 
    "patool",
    "screeninfo", 
    "packaging", 
    "wmi",
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

subprocess.run(command, shell=True)