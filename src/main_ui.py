



import pygame
from controls import Menu
from interface import RUN_RESULT, Runnable


class MainMenu(Menu, Runnable):
    

    __active        : bool = True


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
        super().__init__(title)