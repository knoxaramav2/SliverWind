from __future__ import annotations
from enum import Enum
from random import randint
from tkinter import PhotoImage, StringVar, Tk
from serial import ISerializeable
from ed_util import coall

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

        self.grid = [[None]*height for _ in range(width)]

        for x in range(0, len(self.grid)):
            for y in range(0, len(self.grid[x])):
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

    __zones         : dict
    __current       : GridMap
    __root          : Tk

    def __init__(self, root:Tk):
        self.__zones = {}
        self.__current = None
        self.__root = root

    def set_curr_map(self, map:GridMap):
        self.__current = map

    def curr_map(self):
        return self.__current

    def list_zones(self):
        return list(self.__zones.keys())

    def list_maps(self, zone:str):
        if zone == None: return []
        zn = self.__get_zone(zone)
        if zn == None: return []
        return zn

    def __get_zone(self, zone:str):
        zone = zone.lower()
        if zone not in self.__zones: return None
        return self.__zones[zone]

    def add_zone(self, zone):
        zone = zone.lower()
        if self.__get_zone(zone) != None:
            return
        self.__zones[zone] = []

    def get_map(self, zone:str, map:str):
        zn = self.__get_zone(zone)
        if zn == None: return None
        mp = [t for t in zn if t.name == map]
        if len(mp) == 0: return None
        return mp[0]

    def add_map(self, zone:str, name:str, w:int, h:int):
        zone = zone.lower()
        
        zn = self.__get_zone(zone)
        if zn == None:
            self.add_zone(zone)
        
        if self.get_map(zone, name) != None:
            return None

        map = GridMap(w, h)
        map.name = name
        map.id = randint(100000, 999999)        
        
        self.__zones[zone].append(map)
        self.__current = map
        return map

    def serialize(self):
        return ''

    def deserialize(self, raw:str):
        pass
