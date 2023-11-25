
import pygame
from config import Config, get_config
from save_manager import SaveManager, get_save_manager
from state_broker import BASE_STATES, StateBroker
from window import Window, get_win


class GameCore:


    __cfg       : Config
    __window    : Window
    __broker    : StateBroker
    __s_manager : SaveManager  

    def start(self):
        
        if self.__cfg.dev_start_map != '':
            self.__broker.state = BASE_STATES.DEV_START

        self.__broker.run()

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption('SliverWind')

        self.__cfg = get_config()
        self.__window = get_win()
        self.__broker = StateBroker()
        self.__s_manager = get_save_manager()

__inst__ :GameCore = None

def get_core() -> GameCore:
    global __inst__
    if __inst__ == None:
        __inst__ = GameCore()
    return __inst__