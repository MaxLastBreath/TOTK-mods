import requests

GITHUB = "TOTK-mods"
OWNER = "MaxLastBreath"
url = f"https://api.github.com/repos/MaxLastBreath/TOTK-mods/releases"
search_tag = "manager"

if __name__ == "__main__":
    response = requests.get(url)
    if response.status_code == 200:
        response.raise_for_status()
        release_info = response.json()
    count_linux = 0
    count_windows = 0
    for item in release_info:
        if not item.get("tag_name").startswith(search_tag):
            continue
        print(item.get("tag_name"))
        assets = item.get("assets")
        for item in assets:
            name = item.get("name")
            if name.endswith(".AppImage") or name.startswith("Linux"):
                amount = int(item.get("download_count"))
                print(f"Linux Downloads: {amount}")
                count_linux += amount
            if name.endswith(".exe") or name.startswith("Windows"):
                amount = int(item.get("download_count"))
                print(f"Windows Downloads: {amount}")
                count_windows += amount
    print(f"--TOTAL VERSION COUNT--"
          f"Linux has: {count_linux} Downloads\n"
          f"Windows has {count_windows} Downloads\n"
          f"Total download count is: {count_linux + count_windows}")