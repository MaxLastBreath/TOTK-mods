import sys, os

__ROOT__ = os.path.dirname(__file__)

if getattr(sys, "frozen", False):
    __ROOT__ = sys._MEIPASS
