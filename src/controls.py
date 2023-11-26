from __future__ import annotations
from typing import Callable
import pygame

class Control:

    _bounds        : pygame.Rect   
    _canvas        : pygame.Surface
    _visible       : bool
    
    def hide(self):
        self._visible = False

    def center(self):
        sz = pygame.display.get_window_size()
        self._bounds.centerx = sz[0]/2
        self._bounds.centery = sz[1]/2

    def move(self, pos:tuple[int, int]):
        self._bounds.left = pos[0]
        self._bounds.top = pos[1]

    def show(self):
        self._visible = True

    def update(self):
        if not self._visible: return

        pygame.draw.rect(
            self._canvas,
            (255, 0, 0),
            self._bounds
        )

    def __init__(
            self, canvas:pygame.Surface, 
            pos:tuple[int, int] = (0, 0),
            dim:tuple[int, int] = (1, 1)
            ):
        
        self._canvas = canvas
        self._visible = False
        self._bounds = pygame.Rect(pos[0], pos[1], dim[0], dim[1])

class Container(Control):

    __children      : list[Control]

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
            nx = tl[0] + (((p[0]+1)/(x+2))*width)
            ny = tl[1] + (((p[1]+1)/(y+2))*height)
            c._bounds.center = (nx, ny)

    def __init__(self, 
                 canvas: pygame.Surface, 
                 pos: tuple[int, int] = (0, 0), 
                 dim: tuple[int, int] = (1, 1)):
        super().__init__(canvas, pos, dim)  
        self.__children = []

class Button(Control):

    __callback          : Callable
    __text              : str

    def update(self):
        font = pygame.font.SysFont(None, 30)
        color = (255, 255, 255)
        textobj = font.render(self.__text, 1, color)
        textrect = textobj.get_rect()
        textrect.center = self._bounds.center
        self._canvas.blit(textobj, textrect)


    def on_click(self):
        if not self._visible or self.__callback == None: return
        self.__callback()

    def __init__(
                self, canvas:pygame.Surface, 
                text:str,
                pos:tuple[int, int] = (0, 0),
                dim:tuple[int, int] = (1, 1),
                callback:Callable = None):
        super().__init__(canvas, pos, dim)
        self.__text = text
        self.__callback = callback
        self._visible = True

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

class DevTerminal(Control):


    def execute(self):

        return

    def __init__(self):
        super().__init__()