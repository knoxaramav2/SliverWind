import pygame
from visual_settings import VisualSettings
import visual_settings

class Display:

    __size          : tuple[int, int]
    __settings      : VisualSettings
    __screen        : pygame.Surface

    __click_state   : bool

    def set_size(self, size:(int, int)):
        self.__size = size
        self.__screen = pygame.display.set_mode(self.__size)
        
    def get_size(self):
        return self.__size

    def screen(self):
        return self.__screen

    def is_clicked(self, rect:pygame.Rect):
        mpos = pygame.mouse.get_pos()

        #TODO set by event
        if pygame.mouse.get_pressed()[0] == 1:
            if rect.collidepoint(mpos):
                if self.__click_state == False:
                    self.__click_state = True
                    return True
        else:
            self.__click_state = False

        return False

    def __init__(self):
        pygame.init()
        pygame.time.Clock().tick(24)
        pygame.display.set_caption('Silver Wind')
        
        self.__settings = visual_settings.GetInst()
        self.set_size(self.__settings.size())
        self.__click_state = False
        
        
        
