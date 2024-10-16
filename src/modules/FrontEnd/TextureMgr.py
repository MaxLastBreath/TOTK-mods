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
            image_path="image.jpg", width=int(70 * 1.6), height=int(48 * 1.6)
        )
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
        TextureMgr.CreateTexture(
            image_path="benchmark_korok.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_lookout.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_kakariko.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_great_sky_island.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_goron.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_zora.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_depths.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmarks_first.png",
            width=int(100 * 2.5),
            height=int(40 * 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_border.png",
            width=int(1272 / 3.3),
            height=int(130 / 3.3),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_loading.png",
            width=int(154 / 2.5),
            height=int(150 / 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="benchmark_loading_active.png",
            width=int(154 / 2.5),
            height=int(150 / 2.5),
        )
        TextureMgr.CreateTexture(
            image_path="Legacy_BG.png",
            width=1200,
            height=600,
        )
        TextureMgr.CreateTexture(
            image_path="Ryujinx_BG.png",
            width=1200,
            height=600,
        )
        TextureMgr.CreateTexture(
            image_path="Master_Sword.png",
            width=155,
            height=88,
        )
        TextureMgr.CreateTexture(
            image_path="Master_Sword2.png",
            mirror=True,
            width=155,
            height=88,
        )
        TextureMgr.CreateTexture(
            image_path="Master_Sword_active.png",
            width=int(155 * 1.0),
            height=int(88 * 1.0),
        )
        TextureMgr.CreateTexture(
            image_path="Master_Sword_active2.png",
            mirror=True,
            width=int(155 * 1.0),
            height=int(88 * 1.0),
        )
        TextureMgr.CreateTexture(
            image_path="Hylian_Shield.png",
            width=int(72 * 1.2),
            height=int(114 * 1.2),
        )
        TextureMgr.CreateTexture(
            image_path="Hylian_Shield_Active.png",
            width=int(72 * 1.2),
            height=int(114 * 1.2),
        )
        TextureMgr.CreateTexture(
            image_path="BG_Left_2.png",
            width=1200,
            height=600,
        )
        TextureMgr.CreateTexture(
            image_path="BG_Left_Cheats.png",
            width=1200,
            height=600,
        )
        TextureMgr.CreateTexture(
            image_path="BG_Left.png",
            width=1200,
            height=600,
        )
        TextureMgr.CreateTexture(
            image_path="BG_Right_UI.png",
            width=1200,
            height=600,
        )
        TextureMgr.CreateTexture(
            image_path="image_cheats.png", width=1200, height=600, img_scale=2.0, blur=3
        )
