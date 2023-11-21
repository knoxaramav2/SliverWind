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

class Event:
    transport   : str
    collide     : bool
    script      : str
    script_args : str

    def __init__(self) -> None:
        self.transport = None
        self.collide = True
        self.script = None
        self.script_args = None
    

class Block(ISerializeable):
    
    image       : PhotoImage
    overimage   : PhotoImage
    pos         : tuple[int, int]
    block       : bool
    overdraw    : bool
    event       : Event

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
    grid        : list[list[Block]]
    
    North       : GridMap = None
    South       : GridMap = None
    East        : GridMap = None
    West        : GridMap = None        

    __width     : int
    __height    : int

    def __init__(self, width:int, height:int):
        
        self.__width = width
        self.__height = height

        self.grid = [[None]*width for i in range(height)]

        for y in range(0, height):
            for x in range(0, width):
                self.grid[x][y] = None

    def list_neightbors(self):
        ret = []
        if self.North != None: ret.append(self.North)
        if self.South != None: ret.append(self.South)
        if self.West != None: ret.append(self.West)
        if self.East != None: ret.append(self.East)
        return ret

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

    def get_block(self, x:int, y:int) -> Block:
        x = self.grid[x][y]
        return x
    
    def place_block(self, x:int, y:int, block:Block) -> Block:
        self.grid[x][y] = block
        pass

    def size(self) -> tuple[int,int]:
        return (self.__width, self.__height)

    def serialize(self, raw:str) -> str:
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
