import pyperclip

from configuration.settings import *
from modules.benchmarks import *
import subprocess

def load_UI_elements(manager, canvas):
    # Images and Effects
    canvas.create_image(0, 0, anchor="nw", image=manager.background_image, tags="background")
    canvas.create_image(0, 0, anchor="nw", image=manager.background_LegacyBG, tags="overlay-1")
    canvas.create_image(0, 0, anchor="nw", image=manager.background_UI, tags="overlay")
    canvas.create_image(0, 0, anchor="nw", image=manager.background_UI_element, tags="overlay")

    # Info text BG
    canvas.create_image(0 - scale(20), 0, anchor="nw", image=manager.background_UI3, tags="overlay")

    for location, image in manager.benchmark_dicts.items():
        manager.on_canvas.set_image(
            canvas=canvas,
            row=285, cul=980,
            anchor="c",
            img=image,
            tag=location,
            state="hidden"
        )

    manager.on_canvas.set_image(
        canvas=canvas,
        row=285, cul=980,
        anchor="c",
        img=manager.default_benchmark,
        tag="no_benchmark",
    )

    manager.on_canvas.set_image(
        canvas=canvas,
        row=500, cul=980,
        anchor="c",
        img=manager.benchmark_border,
        tag="benchmark_border",
    )

    manager.on_canvas.image_Button(
        canvas=canvas,
        row=505, cul=980, anchor="c",
        img_1=manager.bench_load_element, img_2=manager.bench_load_element_active,
        command=lambda event: load_benchmark(manager)
    )

    def copy(manager):
        if manager.Curr_Benchmark is None:
            return
        patch_info = manager.ultracam_beyond.get("Keys", [""])
        resolution = manager.UserChoices["resolution"].get()
        shadows = int(manager.UserChoices["shadow resolution"].get().split("x")[0])

        if "aspect ratio" in manager.UserChoices:
            ARR = manager.UserChoices["aspect ratio"].get().split("x")
            Resolution = patch_info["resolution"]["Values"][
                patch_info["resolution"]["Name_Values"].index(resolution)].split("x")
            Resolution = convert_resolution(int(Resolution[0]), int(Resolution[1]), int(ARR[0]),
                                                int(ARR[1]))
            New_Resolution = f"{Resolution[0]}x{Resolution[1]}"
        else:
            New_Resolution = resolution

        system_os = "MacOS" if platform.system() == "Darwin" else platform.system()
        benchmark_result = f"## **{manager.Curr_Benchmark}** Tears Of The Kingdom on {system_os}\n"

        if platform.system() != "Darwin": benchmark_result += f"- **{gpu_name}**\n"
        benchmark_result += (
            f"- **{CPU}**\n"
            f"- **{total_memory}** GB RAM at **{FREQUENCY}** MHz\n"
            f"- **{New_Resolution}** and Shadows: **{shadows}**, FPS CAP: **{manager.UserChoices['fps'].get()}**\n"
            f"## Results:\n"
            f"- Total Frames **{manager.benchmarks[manager.Curr_Benchmark]['Total Frames']}**\n"
            f"- Average FPS **{manager.benchmarks[manager.Curr_Benchmark]['Average FPS']}**\n"
            f"- 1% Lows **{manager.benchmarks[manager.Curr_Benchmark]['1% Low FPS']}** FPS\n"
            f"- 0.1% Lows **{manager.benchmarks[manager.Curr_Benchmark]['0.1% Lowest FPS']}** FPS\n"
        )

        pyperclip.copy(benchmark_result)
    manager.on_canvas.create_label(
        master=manager._window, canvas=canvas,
        text=f"{gpu_name}\n"
              f"{CPU}\n"
              f"Memory: {total_memory}GB {FREQUENCY} MHz",
        description_name="Benchmarks",
        anchor="nw", command=lambda e: copy(manager),
        row=310, cul=820, font=biggyfont, active_fill= "cyan",
        tags=["PC_info"], tag=["PC_info"], outline_tag="PC_info"
    )

    manager.on_canvas.create_label(
        master=manager._window, canvas=canvas,
        text=f"Turn on Direct Keyboard.\n"
             f"Press G after loading in game.\n"
             f"Select your Benchmark in Advanced Settings.\n"
             f"Clicking this text copies your results.\n",
        description_name="Benchmarks",
        anchor="nw", command=lambda e: copy(manager),
        row=400, cul=820, font=biggyfont, active_fill= "cyan",
        tags=["benchmark_info"], tag=["benchmark_info"], outline_tag="benchmark_info"
    )

    # Create Active Buttons.
    manager.on_canvas.image_Button(
        canvas=canvas,
        row=162, cul=794,
        img_1=manager.master_sword_element, img_2=manager.master_sword_element_active, effect_folder="effect1",
        command=lambda event: manager.open_browser("Kofi")
    )

    manager.on_canvas.image_Button(
        canvas=canvas,
        row=162, cul=1007,
        img_1=manager.master_sword_element2, img_2=manager.master_sword_element2_active,
        command=lambda event: manager.open_browser("Github")
    )

    manager.on_canvas.image_Button(
        canvas=canvas,
        row=220, cul=978, anchor="c",
        img_1=manager.hylian_element, img_2=manager.hylian_element_active,
        command=lambda event: manager.open_browser("Discord")
    )

    # Information text.
    manager.on_canvas.create_label(
        master=manager._window, canvas=canvas,
        text=manager.text_content,
        description_name="Info_Label",
        justify="center", anchor="n",
        row=35, cul=975, font=biggyfont,
        tags=["Info_Label"], tag=["Info_Label"], outline_tag="Info_Label"
    )

def create_tab_buttons(manager, canvas):
    if not canvas == manager.maincanvas:
        # Kofi Button
        manager.on_canvas.create_button(
            master=manager._window, canvas=canvas,
            btn_text="Donate", textvariable=manager.switch_text,
            style="success",
            row=1130, cul=520, width=60, padding=10, pos="center",
            tags=["Button"],
            description_name="Kofi",
            command=lambda: manager.open_browser("Kofi")
        )
        # Github Button
        manager.on_canvas.create_button(
            master=manager._window, canvas=canvas,
            btn_text="Github", textvariable=manager.switch_text,
            style="success",
            row=1066, cul=520, width=60, padding=10, pos="center",
            tags=["Button"],
            description_name="Github",
            command=lambda: manager.open_browser("Github")
        )

    # Create tabs

    # Switch mode between Ryujinx and Legacy
    manager.on_canvas.create_button(
        master=manager._window, canvas=canvas,
        btn_text="Switch", textvariable=manager.switch_text,
        style="Danger",
        row=11, cul=138, width=12,
        tags=["Button"],
        description_name="Switch",
        command=manager.switchmode
    )
    # Make the button active for current canvas.
    button1style = "default"
    button2style = "default"
    button3style = "default"
    active_button_style = "secondary"
    try:
        if canvas == manager.maincanvas:
            button1style = active_button_style
        if canvas == manager.cheatcanvas:
            button2style = active_button_style
    except AttributeError as e:
        e = "n"

    # 1 - Main
    manager.on_canvas.create_button(
        master=manager._window, canvas=canvas,
        btn_text="Main",
        style=button1style,
        row=11, cul=26, width=5,
        tags=["Button"],
        description_name="Main",
        command=manager.show_main_canvas
    )
    # 2 - Cheats
    manager.on_canvas.create_button(
        master=manager._window, canvas=canvas,
        btn_text="Cheats",
        style=button2style,
        row=11, cul=77, width=6,
        tags=["Button"],
        description_name="Cheats",
        command=manager.show_cheat_canvas
    )
    # 3 - Settings
    manager.on_canvas.create_button(
        master=manager._window, canvas=canvas,
        btn_text="Settings",
        style=button3style,
        row=11, cul=257, width=8,
        tags=["Button"],
        description_name="Settings",
        command=lambda: manager.setting.settingswindow(manager.constyle, manager.all_canvas)
    )
