


from pygame import Rect
from config import get_config
from world_data import Map, WorldData


class OW_Map:
    
    map         : Map

    north       : Map = None
    south       : Map = None
    east        : Map = None
    west        : Map = None

    rect        : Rect

    def get_pos(self):
        return self.rect.topleft

    def get_dim(self):
        return (self.rect.width, self.rect.height)

    def set_pos(self, x:int, y:int):
        self.rect.topleft = (x, y)

    def __init__(self, map:Map) -> None:
        self.map = map
        sz = get_config().sprite_scale
        w, h = map.get_size()
        w *= sz
        h *= sz
        self.rect = Rect(0, 0, w, h)

class Overworld:

    __world         : WorldData
    __island        : dict

    base            : OW_Map

    def __build_island(self, map:Map, prev:OW_Map=None):
        ow_map = OW_Map(map)
        prev_id = 0 if prev == None else prev.map.id
        print(f'TRAVEL: {prev_id} -> {map.id}')
        self.__island[map.id] = ow_map
        nbs = map.get_neighbors()
        
        for i in range(len(nbs)):
            map_id = nbs[i]

            #Not connected
            if map_id == 0: continue
            #place by prev direction
            elif map_id == prev_id:
                ppos = prev.get_pos()
                pdim = prev.get_dim()
                cdim = ow_map.get_dim()
                #N
                if i == 0: 
                    ow_map.set_pos(ppos[0], ppos[1]+pdim[1])
                    ow_map.north = prev
                    prev.south = ow_map
                #S
                elif i == 1: 
                    ow_map.set_pos(ppos[0], ppos[1]-cdim[1])
                    ow_map.south = prev
                    prev.north = ow_map
                #E
                elif i == 2: 
                    ow_map.set_pos(ppos[0]-cdim[0], ppos[1])
                    ow_map.east = prev
                    prev.west = ow_map
                #W
                elif i == 3: 
                    ow_map.set_pos(ppos[0]+pdim[0], ppos[1])
                    ow_map.west = prev
                    prev.east = ow_map
                continue

            c_map = self.__world.get_by_id(map_id)
            self.__build_island(c_map, ow_map)

        self.base = ow_map

    def __init__(self, world:WorldData) -> None:
        self.__world = world
        self.__island = {}
        self.__build_island(world.get_current())
        pass