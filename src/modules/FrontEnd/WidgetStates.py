from enum import Enum
import string
import random


class ButtonToggle(Enum):
    Dynamic = 0
    Static = 1
    StaticDynamic = 2

class WidgetState(Enum):
    Enter = 0
    Leave = 1

def CreateRandomTag(name: str | None = None) -> str:
    tag = random.choices(string.ascii_uppercase + string.digits, k=8)
    tag = f"{name}".join(tag)
    return tag
