import os
from os.path import dirname, join

class Util:

    base_uri    : str
    save_uri    : str
    rsc_uri     : str
    sprites_uri : str
    fg_uri      : str
    bg_uri      : str
    font_uri    : str
    cfg_uri     : str
    
    def __load_path(self):
        self.base_uri = dirname(dirname(__file__))

        self.rsc_uri = join(self.base_uri, 'rsc')
        self.save_uri = join(self.base_uri, 'saves')
        self.font_uri = join(self.rsc_uri, 'fonts')
        self.fg_uri = join(self.rsc_uri, 'fg')
        self.bg_uri = join(self.rsc_uri, 'bg')
        self.sprites_uri = join(self.rsc_uri, 'sprites')
        self.cfg_uri = join(self.base_uri, 'config')

    def join(self, part1:str, part2:str):
        return join(part1, part2)

    def __init__(self) -> None:
        self.__load_path()
    
__inst__ : Util = None
def GetUtil() -> Util:
    global __inst__
    if __inst__ is None:
        __inst__ = Util()
    return __inst__


