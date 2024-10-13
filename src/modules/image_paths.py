import os
import requests

def Load_ImagePath(Manager):
    m = 2.5
    # Benchmark Images.
    Manager.image_korok = Manager.on_canvas.Photo_Image(
        image_path="benchmark_korok.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.image_Lookout = Manager.on_canvas.Photo_Image(
        image_path="benchmark_lookout.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.image_Kakariko = Manager.on_canvas.Photo_Image(
        image_path="benchmark_kakariko.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.image_GSI = Manager.on_canvas.Photo_Image(
        image_path="benchmark_great_sky_island.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.image_Goron = Manager.on_canvas.Photo_Image(
        image_path="benchmark_goron.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.image_Zora = Manager.on_canvas.Photo_Image(
        image_path="benchmark_zora.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.image_Depths = Manager.on_canvas.Photo_Image(
        image_path="benchmark_depths.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.default_benchmark = Manager.on_canvas.Photo_Image(
        image_path="benchmarks_first.png",
        width=int(100 * m), height=int(40 * m),
    )

    Manager.benchmark_dicts = {
        "Korok Forest": Manager.image_korok,
        "Lookout Landing": Manager.image_Lookout,
        "Kakariko": Manager.image_Kakariko,
        "Great Sky Island": Manager.image_GSI,
        "Goron City": Manager.image_Goron,
        "Depths" : Manager.image_Depths,
        "Zora Domain": Manager.image_Zora,
    }

    # Loading Icons
    m = 3.3
    m_2 = 2.5

    # Benchmark Borders
    Manager.benchmark_border = Manager.on_canvas.Photo_Image(
        image_path="benchmark_border.png",
        width=int(1272 / m), height=int(130/ m),
    )

    Manager.bench_load_element = Manager.on_canvas.Photo_Image(
        image_path="benchmark_loading.png",
        width=int(154/ m_2), height=int(150/ m_2),
    )

    # Benchmark Borders
    Manager.bench_load_element_active = Manager.on_canvas.Photo_Image(
        image_path="benchmark_loading_active.png",
        width=int(154/ m_2), height=int(150/ m_2),
    )

    # Create a Gradiant for Legacy.
    Manager.background_LegacyBG = Manager.on_canvas.Photo_Image(
        image_path="Legacy_BG.png",
        width=1200, height=600,
    )

    # Create a Gradiant for Ryujinx.
    Manager.background_RyuBG = Manager.on_canvas.Photo_Image(
        image_path="Ryujinx_BG.png",
        width=1200, height=600,
    )

    # UI Elements/Buttons
    Manager.master_sword_element = Manager.on_canvas.Photo_Image(
        image_path="Master_Sword.png",
        width=155, height=88,
    )
    Manager.master_sword_element2 = Manager.on_canvas.Photo_Image(
        image_path="Master_Sword2.png", mirror=True,
        width=155, height=88,
    )

    Manager.master_sword_element_active = Manager.on_canvas.Photo_Image(
        image_path="Master_Sword_active.png",
        width=int(155 * 1.0), height=int(88 * 1.0),
    )

    Manager.master_sword_element2_active = Manager.on_canvas.Photo_Image(
        image_path="Master_Sword_active2.png", mirror=True,
        width=int(155 * 1.0), height=int(88 * 1.0),
    )

    Manager.hylian_element = Manager.on_canvas.Photo_Image(
        image_path="Hylian_Shield.png",
        width=int(72 * 1.2), height=int(114 * 1.2),
    )

    Manager.hylian_element_active = Manager.on_canvas.Photo_Image(
        image_path="Hylian_Shield_Active.png",
        width=int(72 * 1.2), height=int(114 * 1.2),
    )

    Manager.background_UI_element = Manager.on_canvas.Photo_Image(
        image_path="BG_Left_2.png",
        width=1200, height=600,
    )

    Manager.background_UI_Cheats = Manager.on_canvas.Photo_Image(
        image_path="BG_Left_Cheats.png",
        width=1200, height=600,
    )

    # Create a Gradiant background.
    Manager.background_UI = Manager.on_canvas.Photo_Image(
        image_path="BG_Left.png",
        width=1200, height=600,
    )

    # Create a transparent black background
    Manager.background_UI3 = Manager.on_canvas.Photo_Image(
        image_path="BG_Right_UI.png",
        width=1200, height=600,
    )

    # Attempt to load images from custom folder.
    if os.path.exists("custom/bg.jpg"):
        image_path = "custom/bg.jpg"
    elif os.path.exists("custom/bg.png"):
        image_path = "custom/bg.png"
    else:
        # Load and set the image as the background
        image_path = "image.png"

    Manager.background_image = Manager.on_canvas.Photo_Image(
        image_path=image_path,
        width=1200, height=600,
        blur=2
    )

    if os.path.exists("custom/cbg.jpg"):
        image_path = "custom/cbg.jpg"
    elif os.path.exists("custom/cbg.png"):
        image_path = "custom/cbg.png"
    else:
        image_path = "image_cheats.png"

    Manager.blurbackground = Manager.on_canvas.Photo_Image(
        image_path=image_path,
        width=1200, height=600, img_scale=2.0,
        blur=3
    )

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
