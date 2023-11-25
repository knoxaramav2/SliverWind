

from enum import Enum
import os


SPRITE_EXT = ['.png', '.jpg', '.jpeg']
SCRIPT_EXT = ['.swrit']
FONT_EXT = ['.ttf']
AUDIO_EXT = ['.mp3', '.aac']

AType = Enum(
    'atype', [
        'audio',
        'sprite',
        'font',
        'script'
    ]
)

class Asset:

    id          : int = 0
    rsc         : any = None
    path        : str
    atype       : AType

    def __load (self):
        
        if self.atype == AType.audio:
            pass
        elif self.atype == AType.sprite:
            pass
        elif self.atype == AType.font:
            pass
        elif self.atype == AType.script:
            pass

    def __init__(self, id:int, path:str, atype:AType):
        self.id = id
        self.path = path
        self.atype = atype
        self.__load()

class AssetManager:
    
    __categories        : dict = {}


    def __init__(self) -> None:
        self.__categories[AType.audio.name] = {}
        self.__categories[AType.sprite.name] = {}
        self.__categories[AType.script.name] = {}
        self.__categories[AType.font.name] = {}
    
    def insert(self, ast:Asset):
        self.__categories[ast.atype.name][ast.id] = ast
    
    def get(self, atype:AType, id:int) -> any:
        return self.__categories[atype.name][id].rsc
    
    def load_from_model(self, raw:str):

        i = raw.find('rsc:')+4
        end = raw.find('\n', i)

        sect = raw[i:end]
        atype = None

        groups = sect.split('|')
        
        for g in groups:
            if g == '': continue
            g_f, g_l = g.split(':', 1)
            _, atype = g_f.split('=')
            colls = g_l.split('@')
            for c in colls:
                if c == '': continue
                _, c_l = c.split(':', 1)
                assets = c_l.split(';')
                for a in assets:
                    if a == '': continue
                    _, atype, path, id = a.split(',')
                    asset = Asset(int(id), path, AType[atype])
                    self.insert(asset)
                    print(f'LOAD ASSET: {asset.atype.name} {os.path.basename(asset.path)}:({asset.id})')
                    
            
        pass
    
__inst__: AssetManager = None
def get_assetmanager():
    global __inst__
    if __inst__ == None:
        __inst__ = AssetManager()
    return __inst__