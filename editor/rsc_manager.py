
import shutil
from tkinter import StringVar, Tk
from ed_util import Util, GetUtil
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

    type        : AType
    name        : str
    path        : str

    def __init__(self, name:str, atype:AType, path:str) -> None:
        self.name = name
        self.type = atype
        self.path = path

class Collection:

    name        : str
    assets      : list[Asset]
    
    def __init__(self, name:str):
        self.name = name
        self.assets = []

class Group:
    
    name        : str
    atype       : AType
    collections : list[Collection]
    col_var     : StringVar

    def __init__(self, name:str, atype:AType, root:Tk):
        self.name = name
        self.atype = atype
        self.collections = []
        self.col_var = StringVar(root)

class RSCManager:

    __asset_groups      : list[Group]

    __util              : Util
    __root              : Tk

    def get_coll_var(self, group:str):
        group = group.lower()
        return self.__group(group).col_var

    def add_coll_var(self, group:str, var):
        group = group.lower()
        self.__group(group).col_var = var
    
    def remove_collection(self, group:str, col:str):
        group = group.lower()
        col = col.lower()

        if col == 'default':
            return False

        path,_ = self.__asset_info(group, col, None)
        shutil.rmtree(path)
        grp = self.__group(group)
        coll = self.__collection(group, col)
        grp.collections.remove(coll)

        return True

    def add_collection(self, group:str, col:str):
        group = group.lower()
        col = col.lower()

        grp = self.__group(group)
        grp.collections.append(Collection(col))

    def collection_exists(self, group:str, col:str):
        group = group.lower()
        col = col.lower()

        grp = self.__group(group)
        return len([t for t in grp.collections if t.name == col]) > 0

    def list_groups(self, atype:AType=None) -> list[str]:
        return [t.name for t in self.__asset_groups if t.atype == atype or atype == None]

    def list_collections(self, group:str):

        group = group.lower()
        grp = self.__group(group)

        return [t.name for t in grp.collections]

    def import_asset(self, src:str, group:str, col:str):
        
        group = group.lower()
        col = col.lower()

        if not os.path.exists(src): return False

        name = os.path.basename(src)
        dst = self.__util.sprites_uri
        ast = AType.sprite
        
        dst, ast = self.__asset_info(group, col, name)

        dirname = os.path.dirname(dst)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        #TODO Add replace option
        if os.path.exists(dst):
            return False

        shutil.copyfile(src, dst)

        self.__collection(group, col).assets.append(Asset(name, ast, dst))

        return True

    def remove_asset(self, group:str, col:str, name:str):

        group = group.lower()
        col = col.lower()
        name = name.lower()

        asset = self.__asset(group, col, name)

        os.remove(asset.path)
        self.__collection(group, col).assets.remove(asset)

    def serialize(self):
        ret = ''
        
        for grp in self.__asset_groups:
            ret += f'{grp.name}={grp.atype.name}:'
            for coll in grp.collections:
                ret += f'{coll.name}:'
                for ast in coll.assets:
                    ret += f'{ast.name},{ast.type.name},{ast.path};'
                ret += '@'
            ret += '|'
        
        return ret[:-1]

    def deserialize(self, valstr:str):
        
        if valstr == None or valstr == '':
            return

        self.__asset_groups = []
        groups = valstr.split('|')
        
        for g in groups:
            if g == '': continue

            g_f, g_l = g.split(':', 1)
            g_name, g_type = g_f.split('=')
            v_group = Group(g_name, AType[g_type], self.__root)
            self.__asset_groups.append(v_group)

            colls = g_l.split('@')
            for c in colls:
                if c == '': continue

                c_f, c_l = c.split(':', 1)
                v_coll = Collection(c_f)
                v_group.collections.append(v_coll)

                assets = c_l.split(';')
                for a in assets:
                    if a == '': continue

                    name, atype, path = a.split(',')
                    v_asset = Asset(name, AType[atype], path)
                    v_coll.assets.append(v_asset)
                    
        pass

    def __group(self, group:str) -> Group:
        return [t for t in self.__asset_groups if t.name == group][0]
    
    def __collection(self, group:str, coll:str) -> Collection:
        grp = self.__group(group)
        return [t for t in grp if t.name == coll][0]

    def __asset(self, group:str, coll:str, ast:str) -> Asset:
        coll = self.__collection(group, coll)
        return [t for t in self.coll if t.name == ast][0]

    def __asset_info(self, group:str, col:str, name:str):
        sgrp = None

        if group == 'audio': 
            dst = self.__util.aud_uri
            ast = AType.audio
        elif group == 'scripts':
            dst = self.__util.script_uri
            ast = AType.script
        elif group == 'fonts':
            dst = self.__util.font_uri
            ast = AType.font
        elif group == 'fg' or 'bg':
            sgrp = group

        ret = self.__util.join(dst, [sgrp, col, name])
        return (ret, ast)

    def __init__(self, root:Tk) -> None:
        
        self.__util = GetUtil()
        self.__root = root

        self.__asset_groups = [
            Group('actor', AType.sprite, self.__root),
            Group('fg', AType.sprite, self.__root),
            Group('bg', AType.sprite, self.__root),
            Group('audio', AType.audio, self.__root),
            Group('script', AType.script, self.__root),
        ]

        for g in self.__asset_groups:
            g.collections.append(Collection('default'))

