from modules.FrontEnd.WidgetStates import *
import ttkbootstrap as ttk
from typing import Callable
from modules.logger import *


class ImageButton:

    _Window: ttk.Window
    _Canvas: ttk.Canvas
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
        tagOn: str,
        tagOff: str,
        Type: ButtonToggle = ButtonToggle.Static,
        isOn: bool = False,
        tags=[],
    ):
        self._Window = window
        self._Canvas = canvas
        self.Name = name
        self.tagOn = tagOn
        self.tagOff = tagOff
        self.Type = Type
        self.IsOn = ttk.BooleanVar(window, False)
        self.FullTags = tags
        self.IsOn.set(isOn)
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
            self.tagOn, "<Button-1>", lambda args: self.ToggleCommand(OnClick, args)
        )
        self._Canvas.tag_bind(
            self.tagOff, "<Button-1>", lambda args: self.ToggleCommand(OnClick, args)
        )

        self._Canvas.tag_bind(
            self.tagOn, "<Enter>", lambda e: self.ActivateImage(WidgetState.Enter)  # fmt:skip
        )
        self._Canvas.tag_bind(
            self.tagOff, "<Leave>", lambda e: self.ActivateImage(WidgetState.Leave)  # fmt:skip
        )

        self._Canvas.tag_bind(
            self.tagOff, "<Enter>", lambda e: self.ActivateImage(WidgetState.Enter)  # fmt:skip
        )
        self._Canvas.tag_bind(
            self.tagOn, "<Leave>", lambda e: self.ActivateImage(WidgetState.Leave)  # fmt:skip
        )

    def SetImageState(self):
        image_On_State = "normal"
        image_Off_State = "hidden"

        if self.get() == True:
            image_On_State = "hidden"
            image_Off_State = "normal"

        self._Canvas.itemconfig(self.tagOn, state=image_On_State)
        self._Canvas.itemconfig(self.tagOff, state=image_Off_State)

    def BindImages(
        self,
        cul: int,
        row: int,
        ImageOn: ttk.PhotoImage,
        ImageOff: ttk.PhotoImage,
        anchor: str = "nw",
    ):

        image_On_State = "normal"
        image_Off_State = "hidden"

        if self.get() == True:
            image_On_State = "hidden"
            image_Off_State = "normal"

        tags = self.FullTags.copy()
        tags.append(self.tagOn)

        self._Canvas.create_image(
            cul,
            row,
            anchor=anchor,
            image=ImageOn,
            state=image_On_State,
            tags=tags,
        )

        tags = self.FullTags.copy()
        tags.append(self.tagOff)

        self._Canvas.create_image(
            cul,
            row,
            anchor=anchor,
            image=ImageOff,
            state=image_Off_State,
            tags=tags,
        )

    def ToggleImg(
        self,
        State: WidgetState,
    ):
        if self.get() is True and self.Type is ButtonToggle.Dynamic:
            if State == WidgetState.Enter:
                self._Canvas.itemconfig(self.tagOn, state="normal")
                self._Canvas.itemconfig(self.tagOff, state="hidden")

            if State == WidgetState.Leave:
                self._Canvas.itemconfig(self.tagOn, state="hidden")
                self._Canvas.itemconfig(self.tagOff, state="normal")
        else:
            if State == WidgetState.Enter:
                self._Canvas.itemconfig(self.tagOn, state="hidden")
                self._Canvas.itemconfig(self.tagOff, state="normal")

            if State == WidgetState.Leave:
                self._Canvas.itemconfig(self.tagOn, state="normal")
                self._Canvas.itemconfig(self.tagOff, state="hidden")

    def ActivateImage(self, State: WidgetState):
        # log.info(f"{self.IsOn.get()}")
        if self.Type == ButtonToggle.StaticDynamic:
            if self.get() is False:
                self.ToggleImg(State)
        else:
            self.ToggleImg(State)
