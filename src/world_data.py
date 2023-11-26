

import os
import typing
from interface import Serializeable

class EventZone:
    pos             : tuple[int, int]
    size            : tuple[int, int]
    on_collide      : bool
    action          : None

    def __init__(self, 
                 x:int, y:int, 
                 w:int, h:int,
                 collide:bool=True,
                 callback:typing.Callable=None 
                 ):
        self.pos = (x, y)
        self.size = (w, h)
        self.on_collide = collide
        self.action = callback


class Cell(Serializeable):

    image_id        : int
    pos             : tuple[int, int]
    block           : bool

    def serialize(self) -> str:
        ret = ''

        return ret
    
    def deserialize(self, raw: str):
        pass

    def __init__(self, 
                 x:int, y:int,
                 block:bool = False,
                 img_id:int = 0
                 ):
        super().__init__()

        self.pos = (x, y)
        self.block = block
        self.image_id = img_id

class Map(Serializeable):

    id              : int
    name            : str
    zone            : str
    __grid          : list[list[Cell]]
    __size          : tuple[int, int]
    __events        : list[EventZone]
    load_script     : int

    __neighbors     : [int] = [0, 0, 0, 0]

    def serialize(self) -> str:
        ret = ''

        return ret
    
    def deserialize(self, raw: str):
        pass

    def set_neighbors(self, n=0, s=0, e=0, w=0):
        if n != 0: self.__neighbors[0] = n
        if s != 0: self.__neighbors[1] = s
        if e != 0: self.__neighbors[2] = e
        if w != 0: self.__neighbors[3] = w

    def get_neighbors(self):
        return self.__neighbors

    def get_size(self) -> tuple[int, int]:
        return self.__size

    def get_cell(self, x:int, y:int) -> Cell:
        return self.__grid[y][x]

    def place_cell(self, cell:Cell):
        x, y = cell.pos
        self.__grid[y][x] = cell

    def __init__(self, name:str, id:int, zone:str, w:int, h:int) -> None:
        super().__init__()
        self.name = name
        self.id = id
        self.zone = zone
        self.__size = (w, h)
        self.__grid = [[None]*w for _ in range(h)]
        self.__events = []
        self.load_script = 0
    
'''
Maintain world/map state
'''
class WorldData(Serializeable):

    __name              : str = ''
    __start_map         : int = 0
    __maps              : dict = {}
    __current_map       : Map = None

    def name(self) -> str: 
        return self.__name

    def get_current(self):
        return self.__current_map

    def set_current(self, zone:str, name:str):
        smap = self.__maps[zone]

        v:Map
        for v in self.__maps.values:
            if v.name == name:
                self.__current_map = v
                return

    def get_by_id(self, id:int):

        for kz, vz in self.__maps.items():
            pass

        pass

    #For new worlds, loads .swc from editor
    def load_world_model(self, raw:str):
        
        start_idx = raw.find('maps:')+4

        #        { ( [
        state = [0,0,0]

        i = start_idx
        size = len(raw) - 1
        buff = ''

        #tmp obj buffers
        curr_map:Map = None
        zone = ''
        map_name = ''
        map_id = 0
        img_id = 0
        onload_id = 0
        ovrimg_id = 0
        block = False
        event = None

        #Neighbor map id's
        neighbors = {'NORTH':0, 'SOUTH':0, 'EAST':0, 'WEST':0}

        x = 0
        y = 0

        while i < size:
            i += 1
            c = raw[i]

            if c == '{': state[0] += 1
            elif c == '}': 
                state[0] -= 1
                #Close map
                if state[0] == 2 and state[1] == 0 and state[2] == 0:
                    curr_map.set_neighbors(
                        n = neighbors['NORTH'],
                        s = neighbors['SOUTH'],
                        e = neighbors['EAST'],
                        w = neighbors['WEST'],
                    )
                    curr_map.load_script = onload_id
                    neighbors = {'NORTH':0, 'SOUTH':0, 'EAST':0, 'WEST':0}
                    print(f'LOAD MAP: {curr_map.zone}:{curr_map.name}:({curr_map.id})')
                    x = 0
                    y = 0
                #End of section
                elif state[0] == 0 and state[1] == 0 and state[2] == 0:
                    break
            elif c == '(': state[1] += 1
            elif c == ')':
                state[1] -= 1
                #MAP ID
                if state[0] == 2 and state[1] == 0:
                    map_name, map_id = buff.split(',')
                #Close cell
                elif state[0] == 3 and state[1] == 0 and state[2] == 1:
                    cell = Cell(x, y, block, img_id)
                    #TODO Overimage
                    #cell.overimage = int(ovrimg_id)
                    #TODO Event
                    #cell.event = ....
                    curr_map.place_cell(cell)
                    x += 1
                    event = None
                buff = ''
            elif c == '[': state[2] += 1
            elif c == ']':#Close row
                state[2] -= 1
                y += 1
                x = 0
            elif c == ':':
                e = i
                if buff == 'ZONE':
                    e = raw.find('=', i)
                    zone = raw[i+1:e]
                elif buff == 'MAP:': pass

                buff = ''
                i = e
            elif c == '=':
                if buff == '': continue
                if buff == 'COL': buff = ''
                #KEY/VAL
                e = raw.find(';', i)
                val = raw[i+1: e]
                #Cell data
                if state[0] == 3 and state[1] == 1 and state[2] == 1:
                    if buff == 'IMG': img_id = int(val)
                    elif buff == 'OVRIMG': ovrimg_id = int(val)
                    elif buff == 'BLOCK': block = val == 'True'
                    elif buff == 'EVENT':
                        if val == '': event = None
                        else:
                            #TODO
                            pass
                #Neightbor id's/DIMS
                if state[0] == 3 and state[1] == 0 and state[2] == 0:
                    if buff == '': continue
                    if buff == 'DIM':
                        w, h = val[1:-1].split(',')
                        w = int(w)
                        h = int(h)
                        map = Map(map_name, int(map_id), zone, w, h)
                        self.__maps[int(map_id)] = map
                        curr_map = map
                    elif buff == 'START':
                        if val == 'True': self.__start_map = int(map_id)
                    elif buff == 'ONLOAD':
                        if val != '': onload_id = int(val)
                    else:
                        neighbors[buff] = int(val)
                buff = ''
                i = e
            else:
                buff += c

        self.__current_map = self.__maps[self.__start_map]

        return True

    def serialize(self) -> str:
        ret = ''

        return ret
        
    def deserialize(self, raw:str):
        
        pass

    def __init__(self):
        pass
