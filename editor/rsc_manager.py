
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

class RSCManager:

    __col_selects         : dict

    __asset_groups      : dict

    __util              : Util
    __root              : Tk

    def get_coll_var(self, group:str):
        group = group.lower()
        return self.__col_selects[group]

    def add_coll_var(self, group:str, var):
        group = group.lower()
        self.__col_selects[group] = var
    
    def remove_collection(self, group:str, col:str):
        group = group.lower()
        col = col.lower()

        if col == 'default':
            return False

        path,_ = self.__asset_info(group, col, None)
        shutil.rmtree(path)
        del self.__asset_groups[group][col]

        return True

    def add_collection(self, group:str, col:str):
        group = group.lower()
        col = col.lower()

        self.__asset_groups[group][col] = {}

    def collection_exists(self, group:str, col:str):
        group = group.lower()
        col = col.lower()

        return col in self.__asset_groups[group]

    def list_collections(self, group:str):

        group = group.lower()

        ret = []
        grp = self.__asset_groups[group]
        for k,v in grp.items():
            ret.append(k)
        
        return ret

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

        self.__asset_groups[group][col][name] = Asset(name, ast, dst)

        return True

    def remove_asset(self, group:str, col:str, name:str):

        group = group.lower()
        col = col.lower()
        name = name.lower()

        asset = self.__asset_groups[group][col][name]
        path,_ = self.__asset_info(group, col, name)

        os.remove(asset.path)
        del self.__asset_groups[group][col][name]

        pass

    def serialize(self):
        ret = 'rsc:'
        for k_grp, v_grp in self.__asset_groups.items():
            ret += f'{k_grp}:'
            for k_col, v_col in v_grp.items():
                ret += f'{k_col}:'
                for k_ast, v_ast in v_col.items():
                    ret += f'{v_ast.name},{v_ast.type.name},{v_ast.path};'
                ret += '@'
            ret += '|'
        
        return ret

    def deserialize(self, valstr:str):
        
        if valstr == None or valstr == '':
            return

        self.__asset_groups = {}
        self.__col_selects = {}

        groups = valstr.split('|')
        for grp_data in groups:
            if grp_data == '': continue
            grp_terms = grp_data.split(':', 1)
            grp_name = grp_terms[0]
            grp_cols = '' if len(grp_terms) == 1 else grp_terms[1]
            self.__asset_groups[grp_name] = {}
            self.__col_selects[grp_name] = StringVar(self.__root, 'default')

            colls = grp_cols.split('@')
            for col_data in colls:
                if col_data == '': continue
                coll_terms = col_data.split(':', 1)
                coll_name = coll_terms[0]
                coll_asts = '' if len(coll_terms) == 1 else coll_terms[1]
                self.__asset_groups[grp_name][coll_name] = {}

                assets = coll_asts.split(';')
                for ast in assets:
                    if ast == '': continue
                    args = ast.split(',')
                    if len(args) != 3:
                        print(f'WRN: Invalid asset: {grp_name}:{coll_name}::{ast}')
                        continue
                    asset = Asset(args[0], args[1], args[2])
                    self.__asset_groups[grp_name][coll_name][args[0]] = asset

    def list_groups(self):
        return list(self.__asset_groups.keys())

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

        self.__col_selects = {}

        self.__asset_groups = {
            'actor':{}, 'fg':{}, 'bg':{}, 'audio':{}, 'script':{}
        }

        for k,v in self.__asset_groups.items():
            v['default'] = {}
            self.__col_selects[k] = StringVar(self.__root, 'default')
