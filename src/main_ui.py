



import pygame
from controls import Menu
from interface import RUN_RESULT, Runnable
from window import Window, get_win


class MainMenu(Menu, Runnable):
    

    __active        : bool = True
    __win           : Window

    #Control

    #Runnable

    def __handle_event(self, e):
        print(e)

    def __loop(self):
        while self.__active:
            for event in pygame.event.get():
                self.__handle_event(event)

    def run(self):
        return RUN_RESULT.OK
    
    def exit(self):
        self.__active =False
    
    def __init__(self, title: str) -> None:
        self.__win = get_win()
        super().__init__(
            self.__win.get_canvas(),
            title)