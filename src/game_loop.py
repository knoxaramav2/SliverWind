

import pygame
from interface import RUN_RESULT, Runnable
from window import Window, get_win


class GameLoop(Runnable):

    __win           : Window
    __active        : bool = True
    __exit_code     : RUN_RESULT = RUN_RESULT.OK

    def __handle_event(self, e):
        pass

    def __loop(self):
        while self.__active:
            for e in pygame.event.get():
                self.__handle_event(e)

    def run(self) -> RUN_RESULT:
        self.__loop()
        return self.__exit_code
    
    def exit(self):
        self.__active = False

    def __init__(self):
        super().__init__()
        
        self.__win = get_win()
