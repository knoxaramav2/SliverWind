
import os


class Profile:

    name            : str = ''
    immortal        : bool = False
    speed           : float = 1.0
    enemy           : bool = False

    sprites         : dict

    def __load(self, path:str):
        if not os.path.exists(path):
            raise Exception(f'Actor sheet not found. ({path})')
        f = open(path, 'r')

        lines = f.readlines()
        for ln in lines:
            ln = ln.strip()
            if ln == '' or ln.startswith('#'): continue
            k,v = ln.split('=')

            match k:
                case 'name': self.name = v
                case 'immortal': self.immortal = bool(int(v))
                case 'speed': self.speed = float(v)
                case 'enemy': self.enemy = bool(int(v))

        f.close()

    def add_sprite(self, name:str, img):

        name, dir, act, num = name.split('_')
        name = name.lower()
        dir = dir.lower()
        act = act.lower()
        num = int(num)

        if act not in self.sprites:
            self.sprites[act] = {}
        if dir not in self.sprites[act]:
            self.sprites[act][dir] = {}
        if num in self.sprites[act][dir]: return
        self.sprites[act][dir][num] = img
        pass

    def load(self, path:str):
        self.__load(path)

    def __init__(self, path:str=None):
        self.sprites = {}
        if path == None:
            return
        self.__load(path)

