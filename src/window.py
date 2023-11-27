from enum import Enum
from random import randint
import pygame
from pygame import Rect
from asset_manager import AType, Asset, AssetManager, get_assetmanager
from config import Config, get_config
from overworld import OW_Map, Overworld
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

    def fade_in(self):
        pass

    def fade_out(self):
        pass

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
    def draw_border(self, rect:Rect, width:int=5, color:tuple=(0,0,255)):
        if not self.__cfg.draw_border: return
        
        x, y, w, h = rect
        pygame.draw.rect(self.__canvas, color, Rect(x, y, w, width))
        pygame.draw.rect(self.__canvas, color, Rect(x, y+h-width, w, width))
        pygame.draw.rect(self.__canvas, color, Rect(x, y, width, h))
        pygame.draw.rect(self.__canvas, color, Rect(x+w-width, y, width, h))

    def __draw_map(self, map:OW_Map, rect:Rect):

        if not self.__cam.in_bounds(map.rect):
            #print(f'Skipped {map.map.name} ({map.map.id})')
            return

        sz = map.map.get_size()
        ss = self.__cfg.sprite_scale
        px, py = rect.topleft

        for x in range(sz[0]):
            for y in range(sz[1]):
                #TODO optomize with blits
                c = map.map.get_cell(x, y)
                ast:Asset = self.__rsc.get_asset_id(AType.sprite, c.image_id)
                pos = (px+ss*x, py+ss*y)
                self.__canvas.blit(ast.rsc, pos)

    def draw_map(self, map:OW_Map, prev:OW_Map = None):
        if map == None: return

        if map.north != prev: 
            self.draw_map(map.north, map)
        if map.south != prev: 
            self.draw_map(map.south, map)
        if map.east != prev: 
            self.draw_map(map.east, map)
        if map.west != prev: 
            self.draw_map(map.west, map)

        mx, my = map.rect.topleft
        w, h = map.rect.width, map.rect.height
        cx, cy = self.__cam.get_pos()
        rect = Rect(mx-cx, my-cy, w, h)
        self.__draw_map(map, rect)
        self.draw_border(rect, color=(randint(0, 255), randint(0, 255), randint(0, 255)))

    '''Recursively render all visible maps on island'''
    def draw_island(self, island:Overworld):
        map = island.base
        self.draw_map(map)
        
    def draw_sprite(self,
                    sprite,
                    pos:tuple[float, float]
                    ):
        sc = self.__cfg.sprite_scale
        #print(f'>> {(pos[0]*sc, pos[1]*sc)}')
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