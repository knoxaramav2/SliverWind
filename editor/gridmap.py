from __future__ import annotations
from enum import Enum
from random import randint
from tkinter import PhotoImage
from serial import ISerializeable

from rsc_manager import Asset

Direction = Enum(
    'direction',[
        'North', 'South', 'East', 'West'
    ]
)

class Block(ISerializeable):
    
    image       : PhotoImage
    overimage   : PhotoImage
    pos         : tuple[int, int]
    block       : bool
    overdraw    : bool
    event       : str

    def __init__(self) -> None:
        self.image = None
        self.overimage = None
        self.pos = (0, 0)
        self.block = False
        self.overdraw = False
        self.event = None

    def serialize(self):
        return ''

    def deserialize(self, raw:str):
        pass


class GridMap(ISerializeable):

    id          : int
    name        : str
    grid        : list[list[Asset]]
    
    North       : GridMap = None
    South       : GridMap = None
    East        : GridMap = None
    West        : GridMap = None        

    __width     : int
    __height    : int

    def __init__(self, width:int, height:int):
        
        self.__width = width
        self.__height = height

        self.grid = [[Block()]*width]*height

        for y in range(0, height):
            for x in range(0, width):
                self.grid[x][y]
        
    def add_neighbor(self, map:GridMap, dir:Direction):
        match dir:
            case Direction.North:
                self.North = map
                map.South = self
            case Direction.South:
                self.South = map
                map.North = self
            case Direction.East:
                self.East = map
                map.West = self
            case Direction.West:
                self.West = map
                map.East = self

    def get_block(self, x:int, y:int):
        return self.grid[x][y]
    
    def place_block(self, x:int, y:int, block:Block):
        self.grid[x][y] = block

    def size(self):
        return (self.__width, self.__height)

    def serialize(self, raw:str):
        return ''

    def deserialize(self):
        return ''

class GridManager(ISerializeable):

    __maps      = [GridMap]
    __current   = GridMap

    def __init__(self):
        self.__maps = []
        self.__current = None

    def curr_map(self):
        return self.__current

    def add_map(self, name:str, w:int, h:int):
        map = GridMap(w, h)
        map.name = name
        map.id = randint(100000, 999999)
        self.__current = map
        return map

    def serialize(self):
        return ''

    def deserialize(self, raw:str):
        pass
