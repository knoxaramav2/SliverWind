from __future__ import annotations
from typing import Callable
import pygame

from util import coall

class Control:

    _bounds        : pygame.Rect   
    _canvas        : pygame.Surface
    _visible       : bool
    _background    : tuple[int, int, int]
    _parent        : Control

    def resize(self, dim:tuple[int,int]=(1, 1), pad:int=5):
        return

    def set_options(self,
            background:tuple[int, int, int]=None
            ):
        self._background = coall(background, self._background)

    def hide(self):
        self._visible = False

    def center(self, rel:pygame.Rect= None):
        if rel != None:
            self._bounds.center = rel.center
            return

        sz = pygame.display.get_window_size()
        self._bounds.centerx = sz[0]/2
        self._bounds.centery = sz[1]/2

    def move(self, pos:tuple[int, int]):
        self._bounds.center = pos

    def show(self):
        self._visible = True

    def update(self):
        if not self._visible: return

        pygame.draw.rect(
            self._canvas,
            self._background,
            self._bounds
        )

    def __init__(
            self, canvas:pygame.Surface,
            pos:tuple[int, int] = (0, 0),
            dim:tuple[int, int] = (1, 1),
            parent:Control=None
            ):
        
        self._canvas = canvas
        self._visible = True
        self._background = (145, 145, 145)
        self._bounds = pygame.Rect(pos[0], pos[1], dim[0], dim[1])
        self._parent = parent

class Container(Control):

    __children      : list[Control]

    def resize(self, pad:int=5):

        w = max([x._bounds.width for x in self.__children])
        h = max([y._bounds.height for y in self.__children])

        self._bounds.width = w + (pad*2)
        self._bounds.height = h + (pad*2)

        pass

    def update(self):
        if not self._visible: return
        super().update()
        for c in self.__children: c.update()

    def add(self, ctrl:Control, x, y):
        ctrl._bounds.center = (x, y)
        self.__children.append(ctrl)

    def pack(self):
        tl = self._bounds.topleft
        width = self._bounds.width
        height = self._bounds.height
        x = max([x._bounds.center[0] for x in self.__children])
        y = max([y._bounds.center[1] for y in self.__children])

        for c in self.__children:
            p = c._bounds.center
            nx = tl[0] + (((p[0]+1)/(x+2))*width) - (c._bounds.width/2)
            ny = tl[1] + (((p[1]+1)/(y+2))*height) - (c._bounds.height/2)
            c.move((nx, ny))

        
        #self.resize()

    def __init__(self, 
                 canvas: pygame.Surface, 
                 pos: tuple[int, int] = (0, 0), 
                 dim: tuple[int, int] = (1, 1)):
        super().__init__(canvas, pos, dim)  
        self.__children = []

class Label(Control):

    __text              : pygame.Surface
    __foreground        : tuple[int, int, int]
    __font              : str
    __size              : int

    _background_off     : bool

    def update(self):
        if not self._visible: return
        if not self._background_off: super().update()
        self._canvas.blit(self.__text, self._bounds.center)
        

    def set_text(self, text:str):
        self.__font = 'arial'
        self.__size = 30
        font = pygame.font.SysFont(self.__font, self.__size)
        self.__text = font.render(text, 1, self.__foreground, self._background)
        #self._bounds = self.__text.get_rect()
        self.move(self.__text.get_rect().center)

    def __init__(self, 
                 canvas: pygame.Surface,
                 text:str,
                 pos: tuple[int, int] = (0, 0),
                 bg_off:bool = False,
                 parent:Control=None):
        super().__init__(canvas, pos, (1,1))
        self._background_off = bg_off
        self.__foreground = (255, 255, 255)
        #self._background = (0, 255, 0)
        self.set_text(text)
        self._parent = parent

class Button(Control):

    __callback          : Callable
    __text              : Label

    def move(self, pos: tuple[int, int]):
        super().move(pos)
        self.__text.move(self._bounds.center)

    def update(self):
        super().update()
        self.__text.update()

    def on_click(self):
        if not self._visible or self.__callback == None: return
        self.__callback()

    def resize(self, pad:int = 5):
        self._bounds.width = self.__text._bounds.width+(2*pad)
        self._bounds.height = self.__text._bounds.height+(2*pad)
        self.__text.move(self._bounds.center)

    def __init__(
                self, canvas:pygame.Surface, 
                text:str,
                pos:tuple[int, int] = (0, 0),
                callback:Callable = None,
                parent:Control=None):
        super().__init__(canvas, pos, (1, 1))
        self.__callback = callback
        self._visible = True
        self.__text = Label(canvas, text, parent=self, bg_off=True)
        self.__text.center(self._bounds)
        self.resize()
        self._background=(0, 0, 255)
        self._parent = parent

class Menu(Container):

    __title         : str
    __canvas        : pygame.Surface

    def show(self):
        super().show()

    def hide(self):
        super().hide()

    def update(self):
        super().update()

    def add(self, ctrl: Control, x, y):
        ctrl._parent = self
        return super().add(ctrl, x, y)
    
    def pack(self):
        return super().pack()

    def __init__(self, canvas:pygame.Surface,
                 text:str,
                 pos:tuple[int, int] = (0, 0),
                 dim:tuple[int, int] = (1, 1)):
        super().__init__(canvas, pos, dim)
        super().center()
        self.__title = text
        self._visible = False

class DevTerminal(Control):


    def execute(self):

        return

    def __init__(self):
        super().__init__()