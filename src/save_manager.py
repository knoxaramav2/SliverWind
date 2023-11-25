
from datetime import datetime
import os
from game_state import GameState, get_gamestate
from util import GetUtil, Util, coall
from world_data import WorldData


class SaveManager:

    __gstate            : GameState
    __target            : str = None
    __util              : Util = None

    def save(self, override_path:str = None):
        if self.__target == None:
            raise Exception('Cannot save file. No target.')
        
        path = coall(override_path, self.__target)
        dir = os.path.dirname(path)
        os.makedirs(dir, exist_ok=True)

        f = open(self.__target, 'w')

        f.write('HEADER::\n')
        f.write('ENGINE_VER=1.0.0\n')
        f.write(f'LAST_WRITE={datetime.now()}\n')
        f.write(f'WORLD={self.__gstate.world.name()}\n')
        f.write('::HEADER\n')
        f.write('WORLD::\n')
        f.write(self.__gstate.serialize()+'\n')
        f.write('::WORLD\n')
        f.flush()
        f.close()

    def __load_sav(self, path):

        f = open(path, 'r')

        state:int = 0

        state_content = ''

        for ln in f.readlines():
            
            if ln == 'HEADER::':
                state = 1
            elif ln == '::HEADER':
                state = 0
            elif ln == 'WORLD::':
                state = 2
            elif ln == '::WORLD':
                state = 0
            else:
                #Header data
                if state == 1:
                    pass
                elif state == 2:
                    print(ln)
                    state_content += ln

            print(ln)
        f.close()

        self.__gstate.deserialize(state_content)

    def __load_model(self, path):
        f = open(path, 'r')
        content = f.read()
        self.__gstate.load_swc(content)
        f.close()

    def load(self, override_path:str = None):
        if self.__target == None:
            raise Exception(f'Cannot load file. No target.')
        
        path:str = coall(override_path, self.__target)
        
        self.__gstate.unload_world()

        ext = path.split('.')[1]
        if ext == 'sav': self.__load_sav(path)
        elif ext == 'swc': self.__load_model(path)

    def set_target(self, name:str):
        basename = name.split('.')[0]
        self.__target = self.__util.join(self.__util.save_uri, [basename, name])

    def __init__(self) -> None:
        self.__util = GetUtil()
        self.__gstate = get_gamestate()


__inst__ :SaveManager = None

def get_save_manager():
    global __inst__
    if __inst__ == None:
        __inst__ = SaveManager()
    return __inst__