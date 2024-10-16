from modules.FrontEnd.CanvasMgr import *


def create_patches(self, row=120, cul_tex=400, cul_sel=550):
    versionvalues = []

    try:
        for key_var, value in self.selected_options.items():
            value = value.get()
            self.old_patches[key_var] = value
    except AttributeError as e:
        self.old_patches = {}

    # Delete the patches before making new ones.
    self.maincanvas.delete("patches")
    # Make UltraCam Patches First.

    UltraCam_Option = "Improve Fog"
    self.fog_var = Canvas_Create.create_checkbutton(
        master=self.window,
        canvas=self.maincanvas,
        text=UltraCam_Option,
        variable="Off",
        row=row + 40,
        cul=cul_tex,
        drop_cul=cul_sel,
        tags=["text"],
        tag="patches",
        description_name="Improve Fog",
    )

    self.selected_options[UltraCam_Option] = self.fog_var
    try:
        if self.old_patches.get(UltraCam_Option) == "On" and not self.old_patches == {}:
            self.fog_var.set("On")
    except AttributeError as e:
        self.old_patches = {}
    row += 40

    # Create labels and enable/disable options for each entry
    for version_option_name, version_option_value in self.version_options[0].items():

        # Create label
        if version_option_name not in ["Source", "nsobid", "offset", "version"]:

            if (
                self.DFPS_var == "UltraCam"
                and version_option_name in self.ultracam_options.get("Skip_Patches")
            ):
                continue

            # Create checkbox
            version_option_var = Canvas_Create.create_checkbutton(
                master=self.window,
                canvas=self.maincanvas,
                text=version_option_name,
                variable="Off",
                row=row + 40,
                cul=cul_tex,
                drop_cul=cul_sel,
                tags=["text"],
                tag="patches",
                description_name=version_option_name,
            )
            self.selected_options[version_option_name] = version_option_var

            try:
                if (
                    self.old_patches.get(version_option_name) == "On"
                    and not self.old_patches == {}
                ):
                    version_option_var.set("On")
            except AttributeError as e:
                self.old_patches = {}

            # Increase +40 space for each patch.
            row += 40

        if row >= 480:
            row = 20
            cul_tex += 180
            cul_sel += 180
