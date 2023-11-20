import os
from datetime import datetime
from ed_util import Util, GetUtil
from rsc_manager import RSCManager

class WorldConfig:

    __dir   : str = None
    __name  : str = None

    __created   : str = None
    __lastwrite : str = None

    last_sprite_dir     : str = ''
    last_aud_dir        : str = ''
    last_script_dir     : str = ''

    __util              : Util
    __rsc               : RSCManager

    def open(self, root):
        if not os.path.exists(self.__dir): return
        path = self.__util.join(self.__dir, self.__name)
        f = open(path, 'r')

        for ln in f.readlines():
            if len(ln.strip()) == 0: continue
            vals = ln.split(':', maxsplit=1)
            k = vals[0].strip()
            v = '' if len(vals) < 2 else vals[1].strip()

            match k:
                case 'created': self.__created = v
                case 'last_write': self.__lastwrite = v
                case 'lsprite': self.last_sprite_dir = v
                case 'laud': self.last_aud_dir = v
                case 'lscript': self.last_script_dir = v
                case 'rsc': self.__rsc.deserialize(v)
                case _: pass

    def save(self):
        exists = os.path.exists(self.__dir)

        if exists:
            print(f'Writing to existing: {self.__name}')
        else:
            print(f'Creating new: {self.__name}')
            os.mkdir(self.__dir)

        content = [
            f'created:{self.__created}\n',
            f'last_write:{datetime.now()}\n',
            f'lsprite:{self.last_sprite_dir}\n',
            f'laud:{self.last_aud_dir}\n',
            f'lscript:{self.last_script_dir}\n',
            f'rsc:{self.__rsc.serialize()}\n'
        ]

        path = self.__util.join(self.__dir, self.__name)
        f = open(path, 'w')
        f.writelines(content)
        f.close()

    def create(self):

        if os.path.exists(self.fullpath()): return

        self.__created = str(datetime.now())
        self.__lastwrite = str(datetime.now())
        self.last_sprite_dir = self.__util.sprites_uri
        self.last_aud_dir = self.__util.aud_uri
        self.last_script_dir = self.__util.script_uri

        self.save()

    def fullpath(self):
        return os.path.join(self.__dir, self.__name)

    def __init__(self, path:str, rman:RSCManager) -> None:
        self.__util = GetUtil()
        self.__rsc = rman

        self.__dir = os.path.dirname(path)
        self.__name = os.path.basename(path)

        self.create()
        

