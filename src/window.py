import pygame
from config import Config, get_config


'''
Control presented graphics
and widgets
'''
class Window:
    
    __canvas        : pygame.Surface
    __cfg           : Config

    def resize(self, w, h):

        if self.__cfg.fullscreen:
            self.__canvas = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.__cfg.win_width, self.__cfg.win_height = pygame.display.get_window_size()
        else:
            self.__cfg.win_width = w
            self.__cfg.win_height = h
            self.__canvas = pygame.display.set_mode((w, h))
        

    def __init_display(self):
        self.resize(self.__cfg.win_width, self.__cfg.win_height)
        self.__canvas.fill((0,0,0))

    def __init__(self) -> None:
        self.__cfg = get_config()
        self.__init_display()
        
__inst__ :Window = None

def get_win():
    global __inst__
    if __inst__ == None:
        __inst__ = Window()
    return __inst__