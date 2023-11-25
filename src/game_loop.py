

import pygame
from game_state import GameState, get_gamestate
from interface import RUN_RESULT, Runnable
from window import Window, get_win
from world_data import WorldData


class GameLoop(Runnable):

    __win           : Window
    __gstate        : GameState
    __world         : WorldData
    __active        : bool = True
    __exit_code     : RUN_RESULT = RUN_RESULT.OK

    def __handle_event(self, e):
        pass

    def __loop(self):
        while self.__active:
            for e in pygame.event.get():
                self.__handle_event(e)

    def draw_background(self):

        pass

    def run(self) -> RUN_RESULT:
        map = self.__world.get_current()
        self.__win.draw_map(map)
        self.__loop()
        return self.__exit_code
    
    def exit(self):
        self.__active = False

    def __init__(self):
        super().__init__()
        
        self.__win = get_win()
        self.__gstate = get_gamestate()
        self.__world = self.__gstate.get_worlddata()
