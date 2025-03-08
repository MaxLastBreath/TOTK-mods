import platform
import subprocess
import os
from configuration.settings import *

latest_version = Version.strip("manager-")
program_name = "NX Optimizer"

def create_zip(source_dir, dest_file):
    with zipfile.ZipFile(dest_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, source_dir)
                zip_path = os.path.join(program_name, relative_path)
                zipf.write(file_path, zip_path)

if __name__ == "__main__":
    if platform.system() == "Windows":
        command = [
            "nuitka",
            "--standalone",
            "--lto=yes",
            "--jobs=4",
            f"--output-filename='{program_name}'",
            "--include-data-dir=GUI=GUI",
            "--include-data-dir=Localization=Localization",
            "--include-data-dir=PatchInfo=PatchInfo",
            "--enable-plugin=tk-inter",
            "--windows-icon=GUI/LOGO.ico"
            "run.py",
        ]

        subprocess.run(command, shell=True)
        os.rename("run.dist", "dist")
        create_zip(
            f"dist/",
            f"dist/{program_name.replace(' ', '_')}_{latest_version}_Windows.zip",
        )

        if os.path.exists(f"dist/{program_name}"):
            os.remove(f"dist/{program_name}")
