
from asset_manager import get_assetmanager
from interface import Serializeable
from world_data import Map, WorldData


class GameState(Serializeable):

    world         : WorldData = None

    #From save file
    def serialize(self):
        ret = ''

        return ret
    
    def deserialize(self, raw:str):
        
        pass
    
    #From world model
    def load_swc(self, content:str):
        self.world = WorldData()
        self.world.load_world_model(content)
        rsc_man = get_assetmanager()
        rsc_man.load_from_model(content)

    def unload_world(self):
        self.world = None

    def __init__(self) -> None:
        super().__init__()


__inst__ :GameState = None
def get_gamestate():
    global __inst__
    if __inst__ == None:
        __inst__ = GameState()
    return __inst__
    