
import os
from PIL import Image, ImageTk
from ed_util import GetUtil, Util


class Icons:

    icons       : dict = {}
    __util      : Util

    def load(self):
        path = self.__util.icon_uri
        files = next(os.walk(path), (None, None, []))[2]
        for f in files:
            name = os.path.basename(f)
            full = self.__util.join(path, name)
            img = Image.open(full).convert('RGBA')
            self.icons[name.split('.')[0]] = (img, full)

    def __init__(self) -> None:
        self.__util = GetUtil()
        self.load()


__inst__ = None
def GetIcons():
    global __inst__
    if __inst__ == None:
        __inst__ = Icons()
    return __inst__

