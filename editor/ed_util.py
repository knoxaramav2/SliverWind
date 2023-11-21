import os
from os.path import dirname, join

def coall(var:str):
    return var if var != None else ''

class Util:

    base_uri    : str
    editor_uri  : str
    defaults_uri: str
    gamedata_uri: str
    icon_uri    : str
    map_uri     : str
    save_uri    : str
    script_uri  : str
    rsc_uri     : str
    sprites_uri : str
    aud_uri     : str
    fg_uri      : str
    bg_uri      : str
    font_uri    : str
    cfg_uri     : str
    
    def __load_path(self, name:str=''):
        name = os.path.basename(name).split('.')[0]
        self.base_uri = dirname(dirname(__file__))
        self.editor_uri = join(self.base_uri, 'editor')
        self.defaults_uri = join(self.editor_uri, 'common')
        self.gamedata_uri = join(self.base_uri, 'gamedata')
        self.map_uri = join(self.gamedata_uri, name)
        
        self.icon_uri = join(self.base_uri, 'editor/icons')
        self.rsc_uri = join(self.map_uri, 'rsc')
        self.sprites_uri = join(self.rsc_uri, 'sprites')
        self.font_uri = join(self.rsc_uri, 'fonts')
        self.fg_uri = join(self.sprites_uri, 'fg')
        self.bg_uri = join(self.sprites_uri, 'bg')
        self.aud_uri = join(self.rsc_uri, 'aud')
        self.script_uri = join(self.rsc_uri, 'scripts')
        self.sprites_uri = join(self.rsc_uri, 'sprites')
        self.cfg_uri = join(self.base_uri, 'config')

    def join(self, part1:str, part2:str|list[str]):
        
        if isinstance(part2, list) == False:
            return join(part1, part2)
        
        for p in part2:
            if p == None: continue
            part1 = join(part1, p)

        return part1

    def set_project_name(self, name:str):
        self.__load_path(name)

    def __init__(self) -> None:
        self.__load_path()
    
__inst__ : Util = None
def GetUtil() -> Util:
    global __inst__
    if __inst__ is None:
        __inst__ = Util()
    return __inst__


