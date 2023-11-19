
import os
import ed_util
from ed_util import GetUtil, Util
from world_config import WorldConfig


class EditorSettings:

    __s_name            : str = ''
    __util              : Util

    def save(self):
        f = open(self.__s_name, 'w')

        f.write(f'recent:{self.last_opened}\n')

        f.flush()
        f.close()

    def __open(self):
        if not os.path.exists(self.__s_name):
            self.save()
        
        f = open(self.__s_name, 'r')
        for ln in f.readlines():
            if len(ln.strip()) == 0: continue
            vals = ln.split(':', maxsplit=1)
            k = vals[0].strip()
            v = '' if len(vals) < 2 else vals[1].strip()

            match k:
                case 'recent': self.last_opened = v
                case _: pass

    def __init__(self):
        self.__util = GetUtil()
        self.__s_name = self.__util.join(self.__util.cfg_uri, 'edconf.cfg')
        
        self.__open()