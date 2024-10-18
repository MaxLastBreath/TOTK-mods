from modules.FrontEnd.WidgetStates import *
import ttkbootstrap as ttk
from typing import Callable
from modules.logger import *


class ImageButton:

    _Window: ttk.Window
    _Canvas: ttk.Canvas
    _Images: list[ttk.PhotoImage]
    Name: str
    IsOn: ttk.BooleanVar
    tagOn: str
    tagOff: str
    Type: ButtonToggle
    FullTags = []

    def __init__(
        self,
        window: ttk.Window,
        canvas: ttk.Canvas,
        name: str,
        Tag: str,
        imagelist: list[ttk.PhotoImage],
        Type: ButtonToggle = ButtonToggle.Static,
        isOn: bool = False,
        tags=[],
    ):
        self._Window = window
        self._Canvas = canvas
        self.Name = name
        self.Tag = Tag
        self.Type = Type
        self.IsOn = ttk.BooleanVar(window, False)
        self.FullTags = tags
        self.IsOn.set(isOn)
        self._Images = imagelist
        # log.info(f"{self.Name}, {self.IsOn.get()} and default : {isOn}")

    def get(self):
        return self.IsOn.get()

    def set(self, isActive: bool):
        self.IsOn.set(isActive)

    def toggle(self):
        if self.IsOn.get() is True:
            self.IsOn.set(False)
        else:
            self.IsOn.set(True)

    def MakeDynamic(self, bool: ButtonToggle):
        self.Type = bool

    def ToggleCommand(self, OnClick: Callable, event: None):
        if callable(OnClick):
            OnClick(event)

        if self.Type == ButtonToggle.StaticDynamic:
            self.toggle()

        if self.Type == ButtonToggle.Dynamic:
            self.toggle()

    def BindCommand(self, OnClick: Callable):
        self._Canvas.tag_bind(
            self.Tag, "<Button-1>", lambda args: self.ToggleCommand(OnClick, args)
        )

        self._Canvas.tag_bind(
            self.Tag, "<Enter>", lambda e: self.ActivateImage(WidgetState.Enter)  # fmt:skip
        )
        self._Canvas.tag_bind(
            self.Tag, "<Leave>", lambda e: self.ActivateImage(WidgetState.Leave)  # fmt:skip
        )

    def SetImageState(self, isOn: bool = False):

        if isOn:
            self._Canvas.itemconfig(self.Tag, state=self.Ima)

    def BindImages(
        self,
        cul: int,
        row: int,
        anchor: str = "nw",
    ):
        tags = self.FullTags.copy()
        tags.append(self.Tag)

        self._Canvas.create_image(
            cul,
            row,
            anchor=anchor,
            image=self._Images[0],
            state="normal",
            tags=tags,
        )

    def ToggleImg(
        self,
        State: WidgetState,
    ):
        if self.get() is True and self.Type is ButtonToggle.Dynamic:
            if State == WidgetState.Enter:
                self._Canvas.itemconfig(self.Tag, image=self._Images[1])

            if State == WidgetState.Leave:
                self._Canvas.itemconfig(self.Tag, image=self._Images[0])
        else:
            if State == WidgetState.Enter:
                self._Canvas.itemconfig(self.Tag, image=self._Images[1])

            if State == WidgetState.Leave:
                self._Canvas.itemconfig(self.Tag, image=self._Images[0])

    def ActivateImage(self, State: WidgetState):
        # log.info(f"{self.IsOn.get()}")
        if self.Type == ButtonToggle.StaticDynamic:
            if self.get() is False:
                self.ToggleImg(State)
        else:
            self.ToggleImg(State)
