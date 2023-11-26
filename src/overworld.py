


from world_data import Map, WorldData


class Overworld:

    __world         : WorldData

    def __travel_map(self, map:Map):
        print(f'TRAVEL: {map.id}')

        nb = map.get_neighbors()
        

        pass

    def __init__(self, world:WorldData) -> None:
        self.__world = world
        self.__travel_map(world.get_current())
        pass