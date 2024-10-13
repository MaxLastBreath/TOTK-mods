from modules.FrontEnd.CanvasMgr import *

class CustomDialog(ttk.Toplevel):
    def __init__(self, parent, title, message, custom_yes = str, custom_no = str, yes_img_1 = None, yes_img_2=None, no_img_1= None, no_img_2= None, width = int, height = int):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry(f"{scale(width)}x{scale(height)}")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_coordinate = (screen_width - self.winfo_reqwidth()) // 2
        y_coordinate = (screen_height - self.winfo_reqheight()) // 2
        self.geometry(f"+{x_coordinate}+{y_coordinate}")

        canvas = ttk.Canvas(self, width=scale(width), height=scale(height))
        canvas.pack()

        self.background = Canvas_Create.Photo_Image(
            image_path="BG_ASK.jpg",
            width=width, height=height,
        )

        canvas.create_image(0, 0, anchor="nw", image=self.background, tags="overlay")

        Canvas_Create.create_label(
                                    master=self, canvas=canvas,
                                    text=message, font=("bahnschrift", 15), color=textcolor,
                                    row=scale(10), anchor="nw", justify="center",
                                    tags=["None"]
                                    )

        if (yes_img_1 is not None and yes_img_2 is not None):
            Canvas_Create.image_Button(
                canvas=canvas,
                row=height - 60, cul=scale(20),
                img_1=yes_img_1, img_2=yes_img_2,
                command=self.on_yes
            )
        else:
            Canvas_Create.create_button(
                master=self, canvas=canvas,
                btn_text=custom_yes,
                row=height-60, cul=scale(20 - (20+80)), width=8,
                style="danger",
                tags=["Ask_Yes"],
                command=self.on_yes
            )
        if (no_img_1 is not None and no_img_2 is not None):
            Canvas_Create.image_Button(
                canvas=canvas,
                row=height - 60, cul=scale(width-(20+scale(no_img_1.width()))),
                img_1=no_img_1, img_2=no_img_2,
                command=self.on_no
            )
        else:
            Canvas_Create.create_button(
                master=self, canvas=canvas,
                btn_text=custom_yes,
                row=height-60, cul=width-(20), width=8,
                style="warning",
                tags=["Ask_No"],
                command=self.on_no
            )

        self.resizable(width=False, height=False)

    def on_yes(self, dummy=None):
        self.destroy()
        self.result = True

    def on_no(self, dummy=None):
        self.destroy()
        self.result = False
