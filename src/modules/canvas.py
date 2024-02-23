import sys
from idlelib.tooltip import Hovertip
from ttkbootstrap import *
from tkinter import *
from PIL import Image, ImageTk, ImageFilter, ImageOps
from configuration.settings import *
import time
import string
import random
import ttkbootstrap as ttk


def next_index(event, var, list=list, increase = 1, command=None):
    value = str(var.get())
    string_list = [str(item) for item in list]
    index = string_list.index(value)
    index += increase
    if index == len(list):
        index = 0
    if index < 0:
        index = len(list) -1
    var.set(list[index])
    if command is not None:
        command(event)

def change_scale(event, var, max, min, increments = int, command=None):
    new_value = float(var.get()) + increments
    if new_value > min:
        new_value = min

    if new_value < max:
        new_value = max

    var.set(str(new_value))
    log.info(new_value)
    if command is not None:
        command(event)
def update_text(event, canvas, name, var):
    var.set(round(float(var.get())))
    canvas.itemconfig(name, text=int(var.get()))

def toggle(event, var):
    if var.get() == "On":
        var.set("Off")
    else:
        var.set("On")

class Canvas_Create:
    def __init__(self):
        self.tooltip = None
        self.window = None
        self.tooltip_active = None
        self.is_Ani_running = True
        self.is_Ani_Paused = False

    def create_combobox(self, canvas,
                        text, master, description_name=None, text_description= None, variable=any, values=[],
                        row=40, cul=40, drop_cul=180, width=150, style="warning",
                        tags=[], tag=None, command=None, is_active=True):
        # create text
        active_color_new = active_color
        if tag is not None:
            tags.append(tag)
        if is_active is False:
            active_color_new = None
        elif is_active is True:
            tags.append("active_text")
        # add outline and user-tag to the outlined text.
        outline_tag = ["outline", tag]
        # create an outline to the text.
        canvas.create_text(
                           scale(cul) + scale(1),
                           scale(row) + scale(1),
                           text=text,
                           anchor="w",
                           fill=outline_color,
                           font=textfont,
                           tags=outline_tag
                           )

        # create the text and the variable for the dropdown.
        new_variable = tk.StringVar(master=master, value=variable)
        text_line = canvas.create_text(
                                       scale(cul),
                                       scale(row),
                                       text=text,
                                       anchor="w",
                                       fill=textcolor,
                                       font=textfont,
                                       tags=tags,
                                       activefil=active_color_new
                                       )

        # create combobox
        dropdown = ttk.Combobox(
                                master=master,
                                textvariable=new_variable,
                                values=values,
                                state="readonly",
                                bootstyle = style,
                                )

        dropdown_window = canvas.create_window(
                                               scale(drop_cul),
                                               scale(row),
                                               anchor="w",
                                               window=dropdown,
                                               width=scale(width),
                                               height=CBHEIGHT,
                                               tags=tag
                                               )
        # bind canvas
        dropdown.bind("<<ComboboxSelected>>", command)
        # attempt to make a Hovertip
        self.read_description(
                              canvas=canvas,
                              option=description_name,
                              text= text_description,
                              position_list=[dropdown, text_line],
                              master=master
                              )
        canvas.tag_bind(text_line, "<Button-1>", lambda event: next_index(event, new_variable, values, 1, command))
        canvas.tag_bind(text_line, "<Button-3>", lambda event: next_index(event, new_variable, values, -1, command))

        row += 40
        return new_variable

    def create_scale(self, canvas,
                        text, master, description_name=None, text_description= None, variable=any, scale_from= 1, scale_to= 100, increments = 5,
                        row=40, cul=40, drop_cul=180, width=150, style="warning",
                        tags=[], tag=None, command=None, is_active=True):
        # create text
        active_color_new = active_color
        if tag is not None:
            tags.append(tag)
        if is_active is False:
            active_color_new = None
        elif is_active is True:
            tags.append("active_text")

        # add outline and user-tag to the outlined text.
        outline_tag = ["outline", tag]
        # create an outline to the text.
        canvas.create_text(
            scale(cul) + scale(1),
            scale(row) + scale(1),
            text=text,
            anchor="w",
            fill=outline_color,
            font=textfont,
            tags=outline_tag
        )
        # create the text and the variable for the dropdown.
        new_variable = tk.StringVar(master=master, value=variable)
        text_line = canvas.create_text(
            scale(cul),
            scale(row),
            text=text,
            anchor="w",
            fill=textcolor,
            font=textfont,
            tags=tags,
            activefil=active_color_new
        )
        update_text_command = lambda event: update_text(event, canvas, text, new_variable)

        master.wm_attributes('-transparentcolor', '#ab23ff')

        # create scale box
        scale_box = ttk.Scale(
            master=master,
            from_=scale_from,
            to=scale_to,
            command=update_text_command,
            length=width,
            style=style,
            variable=new_variable,
        )

        win = canvas.create_window(
            scale(drop_cul),
            scale(row),
            anchor="w",
            window=scale_box,
            width=scale(width),
            height=scale(12),
            tags=tag,
        )

        # bind canvas
        scale_box.bind("<<ComboboxSelected>>", command)
        # attempt to make a Hovertip
        self.read_description(
            canvas=canvas,
            option=description_name,
            position_list=[scale_box, text_line],
            master=master
        )

        tags.append(text)
        outline_tag.append(text)

        # Shows the value from the scale.
        canvas.create_text(
            scale(cul + width + 30) + scale(1),
            scale(row) + scale(1),
            text="NOT SET",
            anchor="w",
            fill=outline_color,
            font=textfont,
            tags=outline_tag
        )

        text_line_value = canvas.create_text(
            scale(cul + width + 30),
            scale(row),
            text="NOT SET",
            anchor="w",
            fill=textcolor,
            font=textfont,
            tags=tags,
            activefil=active_color_new
        )

        self.read_description(
            canvas=canvas,
            option=description_name,
            text= text_description,
            position_list=[scale_box, text_line],
            master=master
        )


        canvas.tag_bind(text_line, "<Button-1>", lambda event: change_scale(event,
                                                                            new_variable,
                                                                            max=scale_from,
                                                                            min=scale_to,
                                                                            increments=increments,
                                                                            command=update_text_command)
                        )
        canvas.tag_bind(text_line, "<Button-3>", lambda event: change_scale(event,
                                                                            new_variable,
                                                                            max=scale_from,
                                                                            min=scale_to,
                                                                            increments=-increments,
                                                                            command=update_text_command)
                        )
        canvas.tag_bind(text_line_value, "<Button-1>", lambda event: change_scale(event,
                                                                            new_variable,
                                                                            max=scale_from,
                                                                            min=scale_to,
                                                                            increments=increments,
                                                                            command=update_text_command)
                        )
        canvas.tag_bind(text_line_value, "<Button-3>", lambda event: change_scale(event,
                                                                            new_variable,
                                                                            max=scale_from,
                                                                            min=scale_to,
                                                                            increments=-increments,
                                                                            command=update_text_command)
                        )

        return new_variable

    def create_checkbutton(
            self, master, canvas,
            text, description_name=None, text_description = None, variable=any,
            row=40, cul=40, drop_cul=180,
            tags=[], tag=None, command=None, is_active=True, style="success"):
        # create text
        active_color_new = active_color
        if tag is not None:
            tags.append(tag)
        if is_active is False:
            active_color_new = None
        elif is_active is True:
            tags.append("active_text")
        # add outline and user-tag to the outlined text.
        outline_tag = ["outline", tag]
        # create an outline to the text.
        canvas.create_text(
                           scale(cul) + scale(1),
                           scale(row) + scale(1),
                           text=text,
                           anchor="w",
                           fill=outline_color,
                           font=textfont,
                           tags=outline_tag
                           )
        # create the text and the variable for the dropdown.
        new_variable = tk.StringVar(master=master, value=variable)
        text_line = canvas.create_text(
                                       scale(cul),
                                       scale(row),
                                       text=text,
                                       anchor="w",
                                       fill=textcolor,
                                       font=textfont,
                                       tags=tags,
                                       activefil=active_color_new
                                       )

        # create checkbutton
        try:
            checkbutton = ttk.Checkbutton(
                                    master=master,
                                    variable=new_variable,
                                    onvalue="On",
                                    offvalue="Off",
                                    state="readonly",
                                    command=command,
                                    bootstyle=style
                                    )
        except Exception as e:
            log.error(e)

        checkbutton_window = canvas.create_window(
                                               scale(drop_cul),
                                               scale(row),
                                               anchor="w",
                                               window=checkbutton,
                                               width = scale(11),
                                               height = scale(11),
                                               tags=tag
                                               )
        # attempt to make a Hover tip
        canvas.tag_bind(text_line, "<Button-1>", lambda event: toggle(event, new_variable))
        self.read_description(
                              canvas=canvas,
                              option=description_name,
                              position_list=[checkbutton, text_line],
                              text=text_description,
                              master=master
                              )
        row += 40
        return new_variable

    def create_button(
            self, master, canvas,
            btn_text, description_name=None, text_description = None, textvariable=None,
            row=40, cul=40, width=None, padding=None, pos="w",
            tags=[], tag=None,
            style="default", command=any,
                      ):

        # create text
        if tag is not None:
            tags.append(tag)
        # create button

        button = ttk.Button(
            master=master,
            text=btn_text,
            command=command,
            textvariable=textvariable,
            bootstyle=style,
            padding=padding
        )

        canvas.create_window(
            scale(cul),
            scale(row),
            width=scale(width*10),
            anchor=pos,
            window=button,
            tags=tags
        )

        self.read_description(
            canvas=canvas,
            option=description_name,
            position_list=[button],
            text=text_description,
            master=master
        )
        return

    def create_label(self, master, canvas,
                        text, description_name=None, text_description = None, font=textfont, color=textcolor, active_fill=None,
                        row=40, cul=40, anchor="w", justify="left",
                        tags=[], tag=None, outline_tag=None, command=None
                     ):
        # create text
        if tag is not None:
            tags.append(tag)
        if command is not None and active_fill is None:
            active_fill = active_color
        # add outline and user-tag to the outlined text.
        if outline_tag is not None:
            outline_tag = [outline_tag, tag]
        # create an outline to the text.
        canvas.create_text(
                           scale(cul) + scale(1),
                           scale(row) + scale(1),
                           text=text,
                           anchor=anchor,
                           justify=justify,
                           fill=outline_color,
                           font=font,
                           tags=outline_tag,
                           )
        # create the text and the variable for the dropdown.
        text_line = canvas.create_text(
                                       scale(cul),
                                       scale(row),
                                       text=text,
                                       anchor=anchor,
                                       justify=justify,
                                       fill=color,
                                       font=font,
                                       tags=tags,
                                       activefil=active_fill,
                                       )
        canvas.tag_bind(text_line, "<Button-1>", command)
        self.read_description(
                              canvas=canvas,
                              option=description_name,
                              position_list=[text_line],
                              text=text_description,
                              master=master
                              )

    def image_Button(self, canvas,
                     row, cul, anchor="nw",
                     img_1=any, img_2=any, effect_folder=None,
                     tag_1=None, tag_2=None,
                     command=None
                     ):
        # If strings are not defined use random tags.
        if tag_1 is None:
            tag_1 = random.choices(string.ascii_uppercase +
                           string.digits, k=8)
            tag_1 = ''.join(tag_1)
        if tag_2 is None:
            tag_2 = random.choices(string.ascii_uppercase +
                           string.digits, k=8)
            tag_2 = ''.join(tag_2)
        # Trigger Animation
        canvas.create_image(scale(cul), scale(row), anchor=anchor, image=img_1, state="normal", tags=tag_1)
        canvas.create_image(scale(cul), scale(row), anchor=anchor, image=img_2, state="hidden", tags=tag_2)

        # Bind the actions for the button.
        canvas.tag_bind(tag_1, "<Enter>", lambda event: self.toggle_img(
                                                                        canvas=canvas, mode="Enter",
                                                                        tag_1=tag_1, tag_2=tag_2,
                                                                        event=event))
        canvas.tag_bind(tag_2, "<Leave>", lambda event: self.toggle_img(
                                                                        canvas=canvas, mode="Leave",
                                                                        tag_1=tag_1, tag_2=tag_2,
                                                                        event=event))
        canvas.tag_bind(tag_2, "<Button-1>", command)
        
        return tag_1, tag_2
        new_folder_path = self.get_UI_path(effect_folder)
        effect_img_list = os.listdir(new_folder_path)
        if effect_folder is not None:
            for item in effect_img_list:
                print(effect_img_list)
                new_item_path = os.path.join(new_folder_path, item)
                effect_img = self.Photo_Image(
                                              image_path=new_item_path,
                                              width=img_1.width(), height=img_1.height(),
                                             )
        return tag_1, tag_2

    def set_image(self, canvas,
                     row, cul, anchor="nw",
                     img=any,
                     tag=None,
                     ):

        if tag is None:
            tag = random.choices(string.ascii_uppercase +
                           string.digits, k=8)
            tag = ''.join(tag)

        canvas.create_image(scale(cul), scale(row), anchor=anchor, image=img, state="normal", tags=tag)

    def toggle_img(self, canvas, mode, tag_1, tag_2, event=None):
        if mode.lower() == "enter":
            canvas.itemconfig(tag_1, state="hidden")
            canvas.itemconfig(tag_2, state="normal")
        if mode.lower() == "leave":
            canvas.itemconfig(tag_1, state="normal")
            canvas.itemconfig(tag_2, state="hidden")

    def read_description(self, canvas, option, text = None, position_list=list, master=any):
        if f"{option}" not in description and text is None:
            return
        for position in position_list:
            try:
                canvas_item = canvas.find_withtag(position)
                if canvas_item:
                    if text is not None:
                        hover = text
                        self.create_tooltip(canvas, position, hover, master)
                    else:
                        hover = description[f"{option}"]
                        self.create_tooltip(canvas, position, hover, master)
                    break
            except TclError as e:
                if text is not None:
                    hover = text
                    Hovertip(position, f"{hover}", hover_delay=Hoverdelay)
                else:
                    hover = text
                    Hovertip(position, f"{hover}", hover_delay=Hoverdelay)

    def create_tooltip(self, canvas, position, hover, master):

        canvas.tag_bind(position, "<Enter>", lambda event: self.show_tooltip(
                                                                             event=event,
                                                                             item=position,
                                                                             tool_text=hover,
                                                                             the_canvas=canvas,
                                                                             master=master
                                                                             )
                        )

        canvas.tag_bind(position, "<Leave>", lambda event: self.hide_tooltip(event=event))
        canvas.tag_bind(position, "<Return>", lambda event: self.hide_tooltip(event))

    def show_tooltip(self, event, item, tool_text, the_canvas, master):
        bbox = the_canvas.bbox(item)
        x, y = bbox[0], bbox[1]
        x += the_canvas.winfo_rootx()
        y += the_canvas.winfo_rooty()

        master.after(50)
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.geometry(f"+{x + scale(20)}+{y + scale(25)}")
        tooltip_label = tk.Label(
                                 master=self.tooltip,
                                 text=tool_text,
                                 background="gray",
                                 relief="solid",
                                 borderwidth=1,
                                 justify="left"
                                 )
        tooltip_label.pack()

        self.tooltip_active = True

    def hide_tooltip(self, event):
        self.tooltip.destroy()
        self.tooltip_active = False

    def focus(self, event):
        # Handle animations and events during those animations.
        self.is_Ani_Paused = False
        
    def un_focus(self, event):
        self.is_Ani_Paused = True

    def on_closing(self, master):
        print("Closing Window")
        self.is_Ani_running = False
        master.destroy()

    def canvas_animation(self, master, canvas):
        master.bind("<Enter>", self.focus)
        master.bind("<Leave>", self.un_focus)
        x = 0
        y = 0
        m = 1
        if sf >= 1.5:
            m *= 2
        if FPS == 0.1:
            m *= 2
        a = scale(m)
        while True:
            if self.is_Ani_running is False:
                return
            if self.is_Ani_Paused is False or get_setting("ani") in ["Off", "Disabled"]:
                if x < 1000:
                    x += m
                    canvas.move("background", -a, 0)
                    time.sleep(FPS)
                if x >= 1000:
                    if y == 0:
                        canvas.move("background", scale(200), scale(300))
                    if y < 300:
                        y += m
                        canvas.move("background", 0, -a)
                        time.sleep(FPS)
                    if y >= 300:
                        x = 0
                        y = 0
                        canvas.move("background", scale(800), 0)
            else:
                time.sleep(0.2)

    def get_UI_path(self, file_name, folder_name="GUI"):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            path = os.path.join(base_path, folder_name, file_name)
            if not os.path.exists(path):
                return file_name
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(base_path)
            path = os.path.join(base_path, folder_name, file_name)
            if not os.path.exists(path):
                return file_name
        return path

    def Photo_Image(self, image_path=str, is_stored=False,
                    width=None, height=None,
                    blur=None, mirror=False, flip=False,
                    auto_contrast=False, img_scale=None):

        UI_path = self.get_UI_path(image_path)
        image = Image.open(UI_path)
        if isinstance(img_scale, int) or isinstance(img_scale, float):
            width = int(width * img_scale)
            height = int(height * img_scale)
        if isinstance(width, int) and isinstance(height, int):
            image = image.resize((scale(width), scale(height)))
        if isinstance(blur, int):
            image = image.filter(ImageFilter.GaussianBlur(blur))
        if mirror is True:
            image = ImageOps.mirror(image)
        if flip is True:
            image = ImageOps.flip(image)
        if auto_contrast is True:
            image = ImageOps.autocontrast(image)
        new_photo_image = ImageTk.PhotoImage(image)
        return new_photo_image

    def effect(self, canvas, img_list=list):
        self.is_effect_active = True
        while True:
            for image in img_list:
                canvas.withtag("effect", state="hidden")
                canvas.withtag(image, state="active")
                time.sleep(0.5)
            if self.is_effect_active is False:
                break

class CustomDialog(ttk.Toplevel):
    def __init__(self, parent, title, message, custom_yes = str, custom_no = str, yes_img_1 = None, yes_img_2=None, no_img_1= None, no_img_2= None, width = int, height = int):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry(f"{scale(width)}x{scale(height)}")

        self.on_canvas = Canvas_Create()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_coordinate = (screen_width - self.winfo_reqwidth()) // 2
        y_coordinate = (screen_height - self.winfo_reqheight()) // 2
        self.geometry(f"+{x_coordinate}+{y_coordinate}")

        canvas = ttk.Canvas(self, width=scale(width), height=scale(height))
        canvas.pack()

        self.background = self.on_canvas.Photo_Image(
            image_path="BG_ASK.png",
            width=width, height=height,
        )

        canvas.create_image(0, 0, anchor="nw", image=self.background, tags="overlay")

        self.on_canvas.create_label(
                                    master=self, canvas=canvas,
                                    text=message, font=("bahnschrift", 15), color=textcolor,
                                    row=scale(10), anchor="nw", justify="center",
                                    tags=["None"]
                                    )

        if (yes_img_1 is not None and yes_img_2 is not None):
            self.on_canvas.image_Button(
                canvas=canvas,
                row=scale(height - (yes_img_1.height()+50)), cul=scale(20),
                img_1=yes_img_1, img_2=yes_img_2,
                command=self.on_yes
            )
        else:
            self.on_canvas.create_button(
                master=self, canvas=canvas,
                btn_text=custom_yes,
                row=scale(height-60), cul=scale(20 - (20+80)), width=8,
                style="danger",
                tags=["Ask_Yes"],
                command=self.on_yes
            )

        if (no_img_1 is not None and no_img_2 is not None):
            self.on_canvas.image_Button(
                canvas=canvas,
                row=scale(height - (no_img_1.height()+50)), cul=scale(width-(20+scale(no_img_1.width()))),
                img_1=no_img_1, img_2=no_img_2,
                command=self.on_no
            )
        else:
            self.on_canvas.create_button(
                master=self, canvas=canvas,
                btn_text=custom_yes,
                row=scale(height-60), cul=scale(width-(20)), width=8,
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
