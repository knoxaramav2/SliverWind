
from pygame import Color, Rect
import pygame
from display import Display
from item import *

class Actor:

    #Meta status
    __immortal      : bool = False
    __paralyzed     : bool = False
    __poisoned      : bool = False
    __blind         : bool = False
    __crippled      : bool = False
    __afraid        : bool = False

    #AI traits
    __follower      : bool = False
    __protective    : float = 0.0
    __aggression    : float = 0.0
    __bravery       : float = 0.0

    #Status
    health          : int = 0
    max_health      : int = 0
    
    mana            : int = 0
    max_mana        : int = 0

    strength        : int = 0
    protection      : int = 0
    speed           : float = 1.0
    speed_mult      : float = 1.0

    stat_fx         : list#List of functions to call on self every update

    #General
    name            : str = 'Bob'
    money           : int = 0
    items           : list[Item] = None

    weapon          : Weapon = None
    armor           : [Armor] = None
    
    #position
    bounding        : Rect

    #dev
    clr           : Color

    def move(self, x:int, y:int):
        if x == 0 and y == 0: return
        dx = x*self.speed*self.speed_mult
        dy = y*self.speed*self.speed_mult
        self.bounding = self.bounding.move(dx, dy)

    def draw(self, dsp:Display):
        pygame.draw.rect(dsp.screen(), self.clr, self.bounding)
        pygame.display.flip()
        

    def update(self):
        for fx in self.stat_fx:
            if fx() == False:#Buff expired
                self.stat_fx.remove(fx)


    def __init__(self) -> None:
            self.stat_fx = []
            self.bounding = Rect(50, 50, 32, 32)
            self.clr = Color(0, 0, 255)

