import pygame
from asset_manager import AType, AssetManager, get_assetmanager
from config import Config, get_config
from world_data import Map


'''
Control presented graphics
and widgets
'''
class Window:
    
    __canvas        : pygame.Surface
    __rsc           : AssetManager
    __cfg           : Config

    def draw_map(self, map:Map):

        dim = map.get_size()
        sc = self.__cfg.sprite_scale

        for y in range(dim[1]):
            for x in range(dim[0]):
                cell = map.get_cell(x, y)
                img = self.__rsc.get(AType.sprite, cell.image_id)
                self.__canvas.blit(img, (x*sc, y*sc))
        pygame.display.flip()

    def draw_sprite(self,
                    sprite,
                    pos:tuple[float, float]
                    ):
        sc = self.__cfg.sprite_scale
        self.__canvas.blit(sprite, (pos[0]*sc, pos[1]*sc))

    def render(self):
        pygame.display.update()

    def clear_screen(self):
        self.__canvas.fill((0,0,0))

    def resize(self, w, h):

        if self.__cfg.fullscreen:
            self.__canvas = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.__cfg.win_width, self.__cfg.win_height = pygame.display.get_window_size()
        else:
            self.__cfg.win_width = w
            self.__cfg.win_height = h
            self.__canvas = pygame.display.set_mode((w, h))
        
    def __init_display(self):
        self.resize(self.__cfg.win_width, self.__cfg.win_height)
        self.clear_screen()

    def __init__(self) -> None:
        self.__cfg = get_config()
        self.__rsc = get_assetmanager()
        self.__init_display()
        
__inst__ :Window = None

def get_win():
    global __inst__
    if __inst__ == None:
        __inst__ = Window()
    return __inst__