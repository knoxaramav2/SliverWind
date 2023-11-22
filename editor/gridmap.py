from __future__ import annotations
from enum import Enum
from random import randint
from tkinter import Tk
from serial import ISerializeable
from ed_util import coall

from rsc_manager import Asset, RSCManager

Direction = Enum(
    'direction',[
        'North', 'South', 'East', 'West'
    ]
)

class Event(ISerializeable):
    transport   : str
    collide     : bool
    script      : Asset
    script_args : str

    def __init__(self):
        self.transport = None
        self.collide = True
        self.script = None
        self.script_args = None

    def serialize(self, rscman:RSCManager):
        ret = '{'

        script_id = 0 if self.script == None else self.script.id

        ret += f'TRNSP={coall(self.transport, "")};'
        ret += f'COLL={self.collide};'
        ret += f'SCRPT={script_id};'
        ret += f'ARGS={coall(self.script_args, "")};'
        
        ret += '}'

        return ret
    
    def deserialize(self):
        pass

class Block(ISerializeable):
    
    image       : Asset
    overimage   : Asset
    pos         : tuple[int, int]
    block       : bool
    event       : Event

    def __init__(self) -> None:
        self.image = None
        self.overimage = None
        self.pos = (0, 0)
        self.block = False
        self.event = None

    def serialize(self, rscman:RSCManager):
        ret = '('
        
        img_id = 0
        over_id = 0
        evnt = ''

        if self.image != None: img_id = self.image.id
        if self.overimage != None: over_id = self.overimage.id
        if self.event != None: evnt = self.event.serialize(rscman)

        ret += f'IMG={img_id};'
        ret += f'OVRIMG={over_id};'
        ret += f'BLOCK={self.block};'
        ret += f'EVENT={evnt};'

        ret += ')'

        return ret

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

    _zone       : str = None

    def __init__(self, width:int, height:int):
        
        self.__width = width
        self.__height = height

        self.grid = [[None]*width for _ in range(height)]

        for y in range(0, len(self.grid)):
            for x in range(0, len(self.grid[y])):
                self.grid[y][x] = None

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
        ret = self.grid[y][x]
        return ret
    
    def place_block(self, x:int, y:int, block:Block) -> Block:
        block.pos = (x, y)
        self.grid[y][x] = block
        pass

    def size(self) -> tuple[int,int]:
        return (self.__width, self.__height)

    def serialize(self, rscman:RSCManager) -> str:
        ret = ''
        
        #Metadata
        ret += f'({self.name},{self.id})={{'
        ret += f'DIM=({self.__width},{self.__height});'
        ret += f'NORTH={0 if self.North == None else self.North.id};'
        ret += f'SOUTH={0 if self.South == None else self.South.id};'
        ret += f'EAST={0 if self.East == None else self.East.id};'
        ret += f'WEST={0 if self.West == None else self.West.id};'
        print(f'Saving {len(self.grid)} x {len(self.grid[0])}')
        #Matrix
        for y in range(len(self.grid)):
            #Rows
            ret += 'COL=['
            for x in range(len(self.grid[y])):
                #Cells in row
                block:Block = self.grid[y][x]
                if block != None:
                    ret += block.serialize(rscman)
                else:
                    ret += '()'
            ret += ']'
        ret += '}'
        return ret

    def deserialize(self, raw:str):
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
        map._zone = zone
        
        self.__zones[zone].append(map)
        self.__current = map
        return map

    def serialize(self, rscman:RSCManager):
        ret = ''

        for zone, maps in self.__zones.items():
            ret += f'ZONE:{zone}={{'
            map:GridMap
            for map in maps:
                ret += 'MAP:{'
                ret += map.serialize(rscman)
                ret += '}'
            ret += '}'
        return ret

    def deserialize(self, raw:str, rsc:RSCManager):
        
        last_zone = ''
        map_name = ''
        map_id = ''

        row = 0
        col = 0

        card_vals = {'NORTH':'0', 'SOUTH':'0', 'EAST':'0', 'WEST':'0'}

        #Cell buffer
        img_id = 0
        ovrimg_id = 0
        block = False
        event = None

        #      {   (  [
        cntr = [0, 0, 0]
        buff = ''
        
        i = -1
        length = len(raw)
        while i < length-1:
            i += 1
            c = raw[i]

            if c == '{':
                cntr[0] += 1
            elif c == '}':
                cntr[0] -= 1
                #Close map
                if cntr[0] == 2 and cntr[1] == 0 and cntr[0] == 0:
                    self.__current.North = card_vals['NORTH']
                    self.__current.South = card_vals['SOUTH']
                    self.__current.East = card_vals['EAST']
                    self.__current.West = card_vals['WEST']

                    col = 0
                    row = 0
            elif c == '(':
                cntr[1] += 1
            elif c == ')':
                cntr[1] -= 1
                if cntr[0] == 2 and cntr[1] == 0:#MAP ID
                    map_name, map_id = buff.split(',')
                elif cntr[0] == 3 and cntr[1] == 0 and cntr[2] == 1:#Add cell
                    b = Block()
                    b.image = rsc.get_asset_by_id(img_id)
                    b.overimage = rsc.get_asset_by_id(ovrimg_id)
                    b.block = block
                    b.event = event
                    self.__current.place_block(col, row, b)
                    col += 1
                    event=None
                buff = ''
            elif c == '[':
                cntr[2] += 1
            elif c == ']':
                cntr[2] -= 1
                row += 1
                col = 0
            elif c == ':':
                if buff == 'ZONE':
                    idx = raw.find('=', i)
                    last_zone = raw[i+1:idx]
                    self.add_zone(last_zone)
                    buff = ''
                    i = idx
                elif buff == 'MAP':
                    buff = ''
            elif c == '=':
                if buff == '': continue
                if buff == 'COL':
                    buff = ''
                else:#KEY=VAL;
                    idx = raw.find(';', i)
                    val = raw[i+1:idx]
                    #Cell data
                    if cntr[0] == 3 and cntr[1] == 1 and cntr[2] == 1:
                        if buff == 'IMG': img_id = int(val)
                        elif buff == 'OVRIMG': ovrimg_id = int(val)
                        elif buff == 'BLOCK': block = val == 'True'
                        elif buff == 'EVENT':
                            if val == '': event = None
                            else:
                                event = Event()
                                idx = raw.find('}', i)
                                trms = raw[i+2:idx].split(';')
                                trms=trms[:-1]
                                for trm in trms:
                                    k,v = trm.split('=')
                                    if k == 'TRNSP': event.transport = v
                                    elif k == 'COLL': event.collide = v == 'True'
                                    elif k == 'SCRPT': event.script = rsc.get_asset_by_id(int(v))
                                    elif k == 'ARGS': event.script_args = v
                                i = idx
                                continue
                                
                    #Cardinal values/dimension
                    if cntr[0] == 3 and cntr[1] == 0 and cntr[2] == 0:
                        if buff == 'DIM':
                            width, height = val[1:-1].split(',')
                            width = int(width)
                            height = int(height)
                            self.add_map(last_zone, map_name, width, height)
                            self.__current.id = map_id
                            col = row = 0
                        else: 
                            card_vals[buff] = int(val)
                    buff = ''
                    i = idx

            else:
                buff += c


        pass
