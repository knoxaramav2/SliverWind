

from enum import Enum
import os

import pygame
from actor_sheet import Profile

from config import get_config


SPRITE_EXT = ['.png', '.jpg', '.jpeg']
SCRIPT_EXT = ['.swrit']
FONT_EXT = ['.ttf']
AUDIO_EXT = ['.mp3', '.aac']

AType = Enum(
    'atype', [
        #System specified
        'audio',
        'sprite',
        'actor',
        'font',
        'script',
        #Name determined
        'anim'
    ]
)

class Asset:

    id          : int = 0
    rsc         : any = None
    path        : str
    name        : str
    atype       : AType

    def __load (self):
        
        if not os.path.exists(self.path):
            print(f'WRN: Cannot find resource for {self.name}. ({self.path})')
            return

        if self.atype == AType.audio:
            pass
        elif self.atype == AType.sprite:
            sc = get_config().sprite_scale
            self.rsc = pygame.image.load(self.path)
            self.rsc = pygame.transform.scale(self.rsc, (sc, sc))
            
        elif self.atype == AType.actor:
            pr = Profile(self.path)
            self.rsc = pr

        elif self.atype == AType.font:
            pass
        elif self.atype == AType.script:
            pass

    def __init__(self, id:int, path:str, atype:AType):
        self.id = id
        self.path = path
        self.name = os.path.basename(path).split('.')[0]
        self.atype = atype
        self.__load()

class AssetManager:
    
    __categories        : dict = {}
    __frwd_buffer       : list

    '''Detect subtype of asset'''
    def __reveal_subtype(self, ast:Asset):
        
        if ast.atype == AType.sprite:
            
            #check for 
            name = os.path.basename(ast.path).split('.')[0]
            if name.count('_') == 3:
                trms = name.split('_')
                if len(trms) != 4: return
                if (trms[2] in ['front', 'back', 'side', 'top', 'bottom'] and
                    trms[3].isnumeric()
                    ):
                    ast.atype = AType.anim

    def __init__(self):
        self.__frwd_buffer = []
        #Audio types
        self.__categories[AType.audio.name] = {}
        #Script types
        self.__categories[AType.script.name] = {}
        self.__categories[AType.actor.name] = {}
        #Fonts
        self.__categories[AType.font.name] = {}
        #Graphics
        self.__categories[AType.sprite.name] = {}
        self.__categories[AType.anim.name] = {}

    def update_profile(self, ast:Asset):
        pr = self.get_asset_name(AType.actor, ast.name.split('_')[0])
        
        if pr == None:
            self.__frwd_buffer.append(ast)
        else:
            pr = pr.rsc
            pr.add_sprite(ast.name, ast.rsc)
        

    def insert(self, ast:Asset):
        self.__reveal_subtype(ast)

        if ast.atype == AType.anim:
            self.update_profile(ast)

        if ast.atype == AType.actor:
            #find buffered sprites
            pr:Profile = ast.rsc
            sprites = [t for t in self.__frwd_buffer if t.name.startswith(ast.name+'_')]
            for sprite in sprites:
                pr.add_sprite(sprite.name, sprite.rsc)

        self.__categories[ast.atype.name][ast.id] = ast

    def get_asset_id(self, atype:AType, id:int) -> Asset:
        cat = self.get_category(atype)
        if cat == None or id not in cat: return None
        return cat[id]

    def get_asset_name(self, atype:AType, name:str) -> Asset:
        cat = self.get_category(atype)
        if cat == None: return None
        r = [t for t in cat.values() if t.name == name]
        return None if len(r) == 0 else r[0]

    def get_category(self, atype:AType):
        return self.__categories[atype.name]

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


class AssetUtil:

    __asset_manager: AssetManager

    def missing_img(self):

        return

    def get_profile(self, name:str) -> Profile:
        ast = self.__asset_manager.get_asset_name(AType.actor, name)
        return None if ast == None else ast.rsc

    #TODO remove?
    def get_spritesheet(self, name:str, action:str, dir:str):
        ct = self.__asset_manager.get_category(AType.anim)
        prefix = f'{name}_{action}_{dir}_'
        return [t for t in ct if t.name.startswith(prefix)]

    def __init__(self):
        self.__asset_manager = get_assetmanager()


__util_inst__: AssetUtil = None
def get_assetutil():
    global __util_inst__
    if __util_inst__ == None:
        __util_inst__ = AssetUtil()
    return __util_inst__

__inst__: AssetManager = None
def get_assetmanager():
    global __inst__
    if __inst__ == None:
        __inst__ = AssetManager()
    return __inst__