from enum import Enum
import pygame
from pygame import Rect
from asset_manager import AType, AssetManager, get_assetmanager
from config import Config, get_config
from world_data import Map


'''
Overworld camera state
'''

CAM_MODE = Enum(
    'cam_mode',[
        'FOLLOW',
        'POINT'
    ]
)

class Camera:

    __bounds    : pygame.Rect

    __cfg       : Config
    __mode      : CAM_MODE

    def in_bounds(self, bounds:Rect):
        return self.__bounds.colliderect(bounds)

    def get_pos(self):
        return self.__bounds.topleft

    def move(self, pos:tuple[int, int]):
        self.__bounds.topleft = pos

    def set_mode(self, mode:CAM_MODE):
        self.__mode = mode

    def __init__(self) -> None:
        self.__mode = CAM_MODE.FOLLOW
        self.__cfg = get_config()
        dim = pygame.display.get_window_size()
        self.__bounds = pygame.Rect(0, 0, dim[0], dim[1])

'''
Control presented graphics
and widgets
'''
class Window:
    
    __canvas        : pygame.Surface
    __rsc           : AssetManager
    __cfg           : Config
    __cam           : Camera

    #Position Modes
    def __local(self, pos:tuple[int, int]):
        return (pos[0]*self.__cfg.sprite_scale, pos[1]*self.__cfg.sprite_scale)
    
    def __global(self, pos:tuple[int, int]):
        ret = pos

        return ret

    #Getters
    def get_canvas(self):
        return self.__canvas

    def get_camera(self):
        return self.__cam
    
    #Render
    def draw_map(self, map:Map):

        dim = map.get_size()
        sc = self.__cfg.sprite_scale
        cx, cy = self.__cam.get_pos()

        return

        for y in range(dim[1]):
            for x in range(dim[0]):
                cell = map.get_cell(x, y)
                img = self.__rsc.get(AType.sprite, cell.image_id)
                #npos = ((x*sc)+cx, (y*sc)+cy)
                nx, ny = self.__local(self.__cam.get_pos())
                npos = ((x*sc)+nx, (y*sc)+ny)
                if x == 0 and y == 0:
                    print(f'<< {npos}')
                self.__canvas.blit(img, npos)
        
    def draw_sprite(self,
                    sprite,
                    pos:tuple[float, float]
                    ):
        sc = self.__cfg.sprite_scale
        print(f'>> {(pos[0]*sc, pos[1]*sc)}')
        #self.__canvas.blit(sprite, (pos[0]*sc, pos[1]*sc))
        pos = (pygame.display.get_window_size())
        pos = (pos[0]/2, pos[1]/2)
        self.__canvas.blit(sprite, pos)

    def render(self):
        pygame.display.update()

    def clear_screen(self):
        self.__canvas.fill((0,0,0))

    #Control
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
        self.__cam = Camera()
        
__inst__ :Window = None

def get_win():
    global __inst__
    if __inst__ == None:
        __inst__ = Window()
    return __inst__