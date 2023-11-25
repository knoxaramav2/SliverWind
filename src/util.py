import os
from os.path import dirname, join

def coall(var, defval=None):
    return var if var != None else defval

class Util:

    #Top Level
    base_uri        : str
    src_uri         : str
    save_uri        : str
    gamedata_uri    : str
    launch_uri      : str
    
    #Engine rsc
    icon_uri        : str
    audio_uri       : str

    #Dev
    dev_save_name   : str

    
    def __load_path(self, name:str=''):
        name = os.path.basename(name).split('.')[0]
        #Top Level
        self.base_uri = dirname(dirname(__file__))
        self.save_uri = join(self.base_uri, 'saves')
        self.gamedata_uri = join(self.base_uri, 'gamedata')
        self.src_uri = join(self.base_uri, 'src')
        self.launch_uri = join(self.src_uri, 'launch.py')

        #Resources
        self.icon_uri = join(self.src_uri, 'editor/icons')
        self.audio_uri = join(self.src_uri, 'audio')

        #Dev
        self.dev_save_name = 'DEV_TMP.sav'

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


