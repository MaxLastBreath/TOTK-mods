import os
import shutil


if __name__ == "__main__":
    with open("git_ignore.txt", "w") as file:
        dir = "Mods"
        path = os.path.join(dir)
        list = os.listdir(path)
        for path in list:
            path = os.path.join(dir, path)
            new_path = os.listdir(path)
            for folder in new_path:
                if folder.endswith(".zip"):
                    continue
                folder_path = os.path.normpath(os.path.join(path, folder))
                file.write(f"scripts\\{folder_path}\n")
                print("Archiving: " + path + folder)
                name = os.path.join(path, folder)
                shutil.make_archive(name, "zip", path, folder)