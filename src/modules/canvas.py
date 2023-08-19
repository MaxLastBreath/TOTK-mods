from idlelib.tooltip import Hovertip
import ttkbootstrap as ttk
from ttkbootstrap import *
from tkinter import *
from configuration.settings import *


class Canvas:
    def __int__(self):
        self.tooltip = None
        self.window = None
        self.tooltip_active = None

    def create_combobox(self, master, canvas, text, row=40, cul=40, drop_cul=180, variable=any,
                        values=[], tags=[], tag=None, description_name=None, command=None):
        # create text
        if tag is not None:
            tags.append(tag)
        # add outline tag.
        outline_tag = tags
        outline_tag.append("outline")
        # create an outline to the text.
        canvas.create_text(
                           scale(cul) + scale(1),
                           scale(row) + scale(1),
                           text=text,
                           anchor="w",
                           fill=outlinecolor,
                           font=textfont,
                           tags=outline_tag
                           )
        # create the text and the variable for the dropdown.
        new_variable = tk.StringVar(value=variable)
        text_line = canvas.create_text(
                                       scale(cul),
                                       scale(row),
                                       text=text,
                                       anchor="w",
                                       fill=textcolor,
                                       font=textfont,
                                       tags=tags
                                       )

        # create comobbox
        dropdown = ttk.Combobox(
                                master=master,
                                textvariable=new_variable,
                                values=values,
                                state="readonly",
                                command=command,
                                )

        dropdown_window = canvas.create_window(
                                               scale(drop_cul),
                                               scale(row),
                                               anchor="w",
                                               window=dropdown,
                                               width=scale(150),
                                               height=CBHEIGHT,
                                               tags=tag
                                               )
        # bind canvas
        dropdown.bind("<<ComboboxSelected>>")
        # attempt to make a Hovertip
        self.read_description(
                              canvas=canvas,
                              option=description_name,
                              position_list=[dropdown, text_line],
                              master=master
                              )
        row += 40
        return new_variable

    def read_description(self, canvas, option, position_list=list, master=any):
        for position in position_list:
            try:
                if f"{option}" in description:
                    canvas_item = canvas.find_withtag(position)
                    if canvas_item:
                        canvas = canvas
                        hover = description[f"{option}"]
                        tooltip = None
                        self.create_tooltip(canvas, position, hover, master)
                        break

            except TclError as e:
                if f"{option}" in description:
                    hover = description[f"{option}"]
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

        master.after(500)
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