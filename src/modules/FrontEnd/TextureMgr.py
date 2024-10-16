from PIL import ImageTk


class Texture:

    Name: str
    Object: ImageTk.PhotoImage

    def __init__(self, Name=str, Object=any):
        self.Name = Name
        self.Object = Object


class TextureMgr:

    TexturePool: list[Texture]

    @classmethod
    def Initialize(cls):
        """Saturates Texture Pool"""

    @classmethod
    def AddTexture(cls, texture: Texture):
        cls.TexturePool.append(texture)

    @classmethod
    def Request(cls, name: str):
        for Entry in cls.TexturePool:
            if name.lower() == Entry.Name.lower():
                return Entry.Object

        raise f"Texture Doesn't exist {name}"
