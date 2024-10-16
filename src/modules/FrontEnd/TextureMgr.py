from PIL import ImageTk
from modules.FrontEnd.CanvasMgr import Canvas_Create


class Texture:

    Name: str
    Object: ImageTk.PhotoImage

    def __init__(self, Name=str, Object=any):
        self.Name = Name
        self.Object = Object


class TextureMgr:

    TexturePool: list[Texture] = []

    @classmethod
    def AppendTexture(cls, texture: Texture):
        cls.TexturePool.append(texture)

    @classmethod
    def Request(cls, Name: str):
        for Entry in cls.TexturePool:
            if Name.lower() == Entry.Name.lower():
                return Entry.Object

        raise f"Texture Doesn't exist {Name}"

    @classmethod
    def CreateTexture(
        cls,
        image_path=str,
        width: int | None = None,
        height: int | None = None,
        blur: int | None = None,
        mirror: bool = False,
        flip: bool = False,
        auto_contrast: bool = False,
        img_scale: int = None,
    ):
        Image = Canvas_Create.Photo_Image(
            image_path, width, height, blur, mirror, flip, auto_contrast, img_scale
        )

        cls.AppendTexture(Texture(image_path, Image))

    @classmethod
    def Initialize(cls):
        TextureMgr.CreateTexture(
            image_path="graphics.png", width=int(70 * 1.6), height=int(48 * 1.6)
        )
        TextureMgr.CreateTexture(
            image_path="graphics_active.png", width=int(70 * 1.6), height=int(48 * 1.6)
        )
        TextureMgr.CreateTexture(
            image_path="extra.png", width=int(70 * 1.6), height=int(48 * 1.6)
        )
        TextureMgr.CreateTexture(
            image_path="extra_active.png", width=int(70 * 1.6), height=int(48 * 1.6)
        )
        TextureMgr.CreateTexture(
            image_path="apply.png", width=int(70 * 1.5), height=int(48 * 1.5)
        )
        TextureMgr.CreateTexture(
            image_path="apply_active.png", width=int(70 * 1.5), height=int(48 * 1.5)
        )
        TextureMgr.CreateTexture(
            image_path="launch.png", width=int(70 * 1.5), height=int(48 * 1.5)
        )
        TextureMgr.CreateTexture(
            image_path="launch_active.png", width=int(70 * 1.5), height=int(48 * 1.5)
        )
        TextureMgr.CreateTexture(
            image_path="extract.png", width=int(70 * 1.5), height=int(48 * 1.5)
        )
        TextureMgr.CreateTexture(
            image_path="extract_active.png", width=int(70 * 1.5), height=int(48 * 1.5)
        )
        TextureMgr.CreateTexture(
            image_path="optimizer_logo.png", width=int(3316 / 10), height=int(823 / 10)
        )
        TextureMgr.CreateTexture(
            image_path="optimizer_logo_active.png",
            width=int(3316 / 10),
            height=int(823 / 10),
        )
