import pygame as pg

from game_controller import GameController
from display import Display

class Core:

    __game_ctrl     : GameController
    __display       : Display

    def exec(self):
        self.__game_ctrl.start()

    def __init__(self):
        self.__display = Display()
        self.__game_ctrl = GameController(self.__display)

if __name__ == "__main__":

    print('Starting...')

    core = Core()
    core.exec()