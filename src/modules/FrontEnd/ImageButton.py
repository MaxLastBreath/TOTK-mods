from modules.FrontEnd.WidgetStates import *
import ttkbootstrap as ttk
from typing import Callable


class ImageButton:

    _Window: ttk.Window
    _Canvas: ttk.Canvas
    Name: str
    IsOn: ttk.BooleanVar
    tagOn: str
    tagOff: str
    Type: ButtonToggle

    def __init__(
        self,
        window: ttk.Window,
        canvas: ttk.Canvas,
        name: str,
        tagOn: str,
        tagOff: str,
        Type: ButtonToggle = ButtonToggle.Static,
        isOn: bool = False,
    ):
        self._Window = window
        self._Canvas = canvas
        self.Name = name
        self.tagOn = tagOn
        self.tagOff = tagOff
        self.Type = Type
        self.IsOn = ttk.BooleanVar(window, isOn)

    def get(self):
        return self.IsOn.get()

    def set(self, isActive: bool):
        self.IsOn.set(isActive)

    def toggle(self):
        if self.IsOn.get() is True:
            self.IsOn.set(False)
        else:
            self.IsOn.set(True)

    def MakeDynamic(self, bool: bool):
        if bool is True:
            self.Type = ButtonToggle.Dynamic
        else:
            self.Type = ButtonToggle.Static

    def ToggleCommand(self, OnClick: Callable, event: None):
        if callable(OnClick):
            OnClick(event)

        if self.Type == ButtonToggle.Dynamic:
            self.toggle()

    def BindCommand(self, OnClick: Callable):

        self._Canvas.tag_bind(
            self.tagOn, "<Button-1>", lambda args: self.ToggleCommand(OnClick, args)
        )
        self._Canvas.tag_bind(
            self.tagOff, "<Button-1>", lambda args: self.ToggleCommand(OnClick, args)
        )

        self._Canvas.tag_bind(
            self.tagOn, "<Enter>", lambda e: self.ActivateImage(WidgetState.Enter)
        )
        self._Canvas.tag_bind(
            self.tagOff, "<Leave>", lambda e: self.ActivateImage(WidgetState.Leave)
        )

    def BindImages(
        self,
        cul: int,
        row: int,
        ImageOn: ttk.PhotoImage,
        ImageOff: ttk.PhotoImage,
        anchor: str = "nw",
    ):
        self._Canvas.create_image(
            cul,
            row,
            anchor=anchor,
            image=ImageOn,
            state="normal",
            tags=self.tagOn,
        )

        self._Canvas.create_image(
            cul,
            row,
            anchor=anchor,
            image=ImageOff,
            state="hidden",
            tags=self.tagOff,
        )

    def ToggleImg(self, State: WidgetState):
        if State == WidgetState.Enter:
            self._Canvas.itemconfig(self.tagOn, state="hidden")
            self._Canvas.itemconfig(self.tagOff, state="normal")

        if State == WidgetState.Leave:
            self._Canvas.itemconfig(self.tagOn, state="normal")
            self._Canvas.itemconfig(self.tagOff, state="hidden")

    def ActivateImage(self, State: WidgetState):
        if self.Type == ButtonToggle.Dynamic:
            if self.get() is False:
                self.ToggleImg(State)
        else:
            self.ToggleImg(State)
