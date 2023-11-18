from enum import Enum
from os import walk

import pygame

import util

FontNames = Enum(
    'name', [
    ]
)

class Fonts:

    fonts       : []

    def __init__(self) -> None:
        utl = util.GetUtil()
        f_path = utl.font_uri
        fonts = next(walk(f_path), (None, None, []))[2]
        fonts = [f for f in fonts if f.endswith('.ttf')]
        
        self.fonts = []
        for f in fonts:
            self.fonts.append(pygame.font.Font(f, 16))


__inst__ : Fonts = None

def GetInst() -> Fonts:
    global __inst__
    if __inst__ == None:
        __inst__ = Fonts()
    return __inst__