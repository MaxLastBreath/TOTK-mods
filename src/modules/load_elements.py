from configuration.settings import *
import subprocess

def load_UI_elements(self, canvas):
    # Images and Effects
    canvas.create_image(0, 0, anchor="nw", image=self.background_image, tags="background")
    canvas.create_image(0, 0, anchor="nw", image=self.background_LegacyBG, tags="overlay-1")
    canvas.create_image(0, 0, anchor="nw", image=self.background_UI, tags="overlay")
    canvas.create_image(0, 0, anchor="nw", image=self.background_UI_element, tags="overlay")

    # Info text BG
    canvas.create_image(0 - scale(20), 0, anchor="nw", image=self.background_UI3, tags="overlay")

    for location, image in self.benchmark_dicts.items():
        self.on_canvas.set_image(
            canvas=canvas,
            row=285, cul=980,
            anchor="c",
            img=image,
            tag=location,
            state="hidden"
        )

    self.on_canvas.set_image(
        canvas=canvas,
        row=285, cul=980,
        anchor="c",
        img=self.default_benchmark,
        tag="no_benchmark",
    )

    def copy(self):
        if self.Curr_Benchmark is None:
            return
        log.info(self.Curr_Benchmark)
        benchmark_result = (f"Benchmark For: **{self.mode}** Tears Of The Kingdom\n"
                            f"**{gpu_name}**\n"
                            f"**{CPU}**\n"
                            f"**{total_memory}** GB RAM at **{FREQUENCY}** MHz\n"
                            f"**{self.Curr_Benchmark}** Results:\n"
                            f"Total Frames **{self.benchmarks[self.Curr_Benchmark]['Total Frames']}**\n"
                            f"Average FPS **{self.benchmarks[self.Curr_Benchmark]['Average FPS']}**\n"
                            f"1% Lows **{self.benchmarks[self.Curr_Benchmark]['1% Low FPS']}** FPS\n"
                            f"0.1% Lows **{self.benchmarks[self.Curr_Benchmark]['0.1% Lowest FPS']}** FPS\n"
                            )

        subprocess.run(['clip'], input=benchmark_result.strip().encode('utf-16'), check=True)

    self.on_canvas.create_label(
        master=self.window, canvas=canvas,
        text=f"{gpu_name}\n"
              f"{CPU}\n"
              f"Memory: {total_memory}GB {FREQUENCY} MHz",
        description_name="Benchmarks",
        anchor="nw", command=lambda e: copy(self),
        row=310, cul=820, font=biggyfont, active_fill= "cyan",
        tags=["PC_info"], tag=["PC_info"], outline_tag="PC_info"
    )

    self.on_canvas.create_label(
        master=self.window, canvas=canvas,
        text=f"Turn on Direct Keyboard.\n"
             f"Press G after loading in game.\n"
             f"Select your Benchmark in Advanced Settings.\n"
             f"Clicking this text copies your results.\n",
        description_name="Benchmarks",
        anchor="nw", command=lambda e: copy(self),
        row=400, cul=820, font=biggyfont, active_fill= "cyan",
        tags=["benchmark_info"], tag=["benchmark_info"], outline_tag="benchmark_info"
    )

    # Create Active Buttons.
    self.on_canvas.image_Button(
        canvas=canvas,
        row=162, cul=794,
        img_1=self.master_sword_element, img_2=self.master_sword_element_active, effect_folder="effect1",
        command=lambda event: self.open_browser("Kofi")
    )

    self.on_canvas.image_Button(
        canvas=canvas,
        row=162, cul=1007,
        img_1=self.master_sword_element2, img_2=self.master_sword_element2_active,
        command=lambda event: self.open_browser("Github")
    )

    self.on_canvas.image_Button(
        canvas=canvas,
        row=220, cul=978, anchor="c",
        img_1=self.hylian_element, img_2=self.hylian_element_active,
        command=lambda event: self.open_browser("Discord")
    )

    # Information text.
    self.on_canvas.create_label(
        master=self.window, canvas=canvas,
        text=self.text_content,
        description_name="Info_Label",
        justify="center",
        row=93, cul=1001 - 153, font=biggyfont,
        tags=["Info_Label"], tag=["Info_Label"], outline_tag="Info_Label"
    )

def create_tab_buttons(self, canvas):
    if not canvas == self.maincanvas:
        # Kofi Button
        self.on_canvas.create_button(
            master=self.window, canvas=canvas,
            btn_text="Donate", textvariable=self.switch_text,
            style="success",
            row=1130, cul=520, width=60, padding=10, pos="center",
            tags=["Button"],
            description_name="Kofi",
            command=lambda: self.open_browser("Kofi")
        )
        # Github Button
        self.on_canvas.create_button(
            master=self.window, canvas=canvas,
            btn_text="Github", textvariable=self.switch_text,
            style="success",
            row=1066, cul=520, width=60, padding=10, pos="center",
            tags=["Button"],
            description_name="Github",
            command=lambda: self.open_browser("Github")
        )

    # Create tabs

    # Switch mode between Ryujinx and Legacy
    self.on_canvas.create_button(
        master=self.window, canvas=canvas,
        btn_text="Switch", textvariable=self.switch_text,
        style="Danger",
        row=11, cul=138, width=12,
        tags=["Button"],
        description_name="Switch",
        command=self.switchmode
    )
    # Make the button active for current canvas.
    button1style = "default"
    button2style = "default"
    button3style = "default"
    active_button_style = "secondary"
    try:
        if canvas == self.maincanvas:
            button1style = active_button_style
        if canvas == self.cheatcanvas:
            button2style = active_button_style
    except AttributeError as e:
        e = "n"

    # 1 - Main
    self.on_canvas.create_button(
        master=self.window, canvas=canvas,
        btn_text="Main",
        style=button1style,
        row=11, cul=26, width=5,
        tags=["Button"],
        description_name="Main",
        command=self.show_main_canvas
    )
    # 2 - Cheats
    self.on_canvas.create_button(
        master=self.window, canvas=canvas,
        btn_text="Cheats",
        style=button2style,
        row=11, cul=77, width=6,
        tags=["Button"],
        description_name="Cheats",
        command=self.show_cheat_canvas
    )
    # 3 - Settings
    self.on_canvas.create_button(
        master=self.window, canvas=canvas,
        btn_text="Settings",
        style=button3style,
        row=11, cul=257, width=8,
        tags=["Button"],
        description_name="Settings",
        command=lambda: self.setting.settingswindow(self.constyle, self.all_canvas)
    )
