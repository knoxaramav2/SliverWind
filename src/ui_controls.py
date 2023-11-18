#Specify common UI controls

import pygame
from pygame import Color, Rect, Surface
from display import Display
import util

class Control:

    size        : tuple[int, int]
    parent      : any
    img         : any
    rect        : Rect
    font        : any

    def draw(self, surface:Surface):
        pass

    def set_parent(self, parent):
        self.parent = parent

    def __init__(self, parent):
        self.parent = parent


class Button(Control):

    __text      : Surface
    __txt_rect  : Rect
    __fnc       : any

    def click(self):
        if self. __fnc == None: return

        self.__fnc()

    def draw(self, dsp:Display):
        
        surface = dsp.screen()
        surface.blit(self.img, (self.rect.x, self.rect.y))
        surface.blit(self.__text, (self.__txt_rect.x, self.__txt_rect.y))

        if dsp.is_clicked(self.rect):
            self.click()

    def __init__(self, 
                 parent, pos: tuple[int, int], 
                 size: tuple[int, int],
                 text:str, fnc = None):
        
        #Center
        pos = (pos[0]-size[0]/2,pos[1]-size[1]/2)

        super().__init__(parent)
        
        utl = util.GetUtil()

        img = pygame.image.load(utl.join(utl.rsc_uri, 'border1.png')).convert_alpha()
        img = pygame.transform.scale(img, size)
        self.img = img
        self.rect = img.get_rect()
        self.rect.topleft = pos

        self.__fnc = fnc
        font = pygame.font.SysFont("arialblack", 40)
        self.__text = font.render(text, True, Color(255,255,255))
        self.__txt_rect = self.__text.get_rect()
        self.__txt_rect.topleft = (pos[0]+(size[0]-self.__txt_rect[2])/2 ,pos[1]+(size[1]-self.__txt_rect[3])/2)

class Slider(Control):

    def __init__(self, parent, txt:str):
        super().__init__(parent)


class Toggle:

    def __init__(self):
        pass

class TextInput:

    def __init__(self):
        pass

class Label(Control):

    __text      : Surface

    def draw(self, dsp:Display):
        surface = dsp.screen()
        surface.blit(self.__text, (self.rect.x, self.rect.y))

    def __init__(self, 
                 parent: Control, pos: tuple[int, int], text:str):
        
        super().__init__(parent)

        font = pygame.font.SysFont("arialblack", 80)
        self.__text = font.render(text, True, Color(200,200,200))
        self.rect = self.__text.get_rect()
        self.rect.topleft = (pos[0]-self.rect[2]/2, pos[1])

class Menu(Control):

    __children      : list[Control]

    def add_child(self, child:Control):
        if child in self.__children: return
        child.set_parent(self)
        self.__children.append(child)

    def __init__(self, 
                 parent, pos: tuple[int, int], 
                 size: tuple[int, int]):
        super().__init__(parent)
        self.rect = Rect(pos[0], pos[1], size[0], size[1])






