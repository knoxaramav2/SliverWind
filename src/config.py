
import sys


class Config:

    #Dims
    win_width           : int = 640
    win_height          : int = 480
    fullscreen          : bool = False

    #Dev stuff
    dev_mode            : bool = False
    dev_god_mode        : bool = False
    dev_start_map       : str = None
    dev_save_file       : str = None

    def __parse_cli(self):
        args = sys.argv

        for arg in args:
            trms = arg.split('=')
            k = trms[0]
            v = '' if len(trms) == 1 else trms[1]

            match k:
                case '--width': self.win_width=int(v)
                case '--height': self.win_width=int(v)
                case '--fullscreen': self.fullscreen = True

                case '-d': self.dev_mode = True
                case '-g': self.dev_god_mode = self.dev_mode = True
                case '--startmap': self.dev_start_map = v
                case '--save': self.dev_save_file = v

    def __init__(self) -> None:
        self.__parse_cli()

__inst__ :Config = None

def get_config() -> Config:
    global __inst__
    if __inst__ == None:
        __inst__ = Config()
    return __inst__