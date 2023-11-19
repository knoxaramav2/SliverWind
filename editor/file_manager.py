
import os
from os.path import dirname, join
from ed_util import GetUtil, Util
from rsc_manager import RSCManager
from world_config import WorldConfig


class FileManager:

    __def_dirs      : list[str]
    __proj_dir      : str

    __rsc           : RSCManager
    __util          : Util

    def __create_def_dirs(self):
        
        for d in self.__def_dirs:
            path = self.__util.join(self.__proj_dir, d)
            os.makedirs(path, exist_ok=True)

    def load_world(self, name):
        self.__proj_dir = self.__util.map_uri

    def new_world(self, name) -> WorldConfig:
        self.__proj_dir = self.__util.map_uri

        self.__create_def_dirs()

        path = join(self.__proj_dir, name+'.swc')
        world_cfg = WorldConfig(path, self.__rsc)
        world_cfg.create()

        return world_cfg

    def __init__(self, rman:RSCManager) -> None:
        self.__rsc = rman
        self.__util = GetUtil()
        self.__def_dirs =[
            'rsc', 'rsc/sprites', 'rsc/sprites/fg', 'rsc/sprites/bg', 'rsc/audio',
            'rsc/scripts', 'rsc/fonts', 'maps', 'meta'
        ]