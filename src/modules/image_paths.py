from modules.FrontEnd.CanvasMgr import *
from modules.FrontEnd.TextureMgr import TextureMgr
import os
import requests


def Load_ImagePath(Manager):

    # Handle Text Window
    def fetch_text_from_github(file_url):
        try:
            response = requests.get(file_url)
            if response.status_code == 200:
                return response.text
            else:
                log.error("Error: Unable to fetch text from Github")
        except requests.exceptions.RequestException as e:
            log.error(f"Error occurred while fetching text: {e}")

        return ""

    # Information text
    file_url = "https://raw.githubusercontent.com/MaxLastBreath/TOTK-mods/main/scripts/Announcements/Announcement%20Window.txt"
    Manager.text_content = fetch_text_from_github(file_url)
    # Info Element
