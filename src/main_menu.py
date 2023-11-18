###############################
#Main menu
###############################

from enum import Enum
import pygame
from display import Display

from ui_controls import Button, Label, Menu
import visual_settings

MenuMode = Enum(
    'mode',[
        'Main',
        'Settings'
    ]
)

class MainMenu:

    __menu          : Menu
    __settings      : Menu
    __mode          : MenuMode
    __active        : bool
    __menu_btns     : list[Button]
    __settings_btns : list[Button]
    __title         : Label
    __display       : Display
    __play          : bool

    def renderMain(self):
        self.__display.screen().fill((52, 78, 91))
        for b in self.__menu_btns:
            b.draw(self.__display)
        self.__title.draw(self.__display)

    def renderSettings(self):
        self.__display.screen().fill((32, 58, 71))
        for b in self.__settings_btns:
            b.draw(self.__display)

    def loop(self):
        while self.__active:
            if self.__mode == MenuMode.Main:
                self.renderMain()
                pygame.event.clear()
            elif self.__mode == MenuMode.Settings:
                self.renderSettings()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.__mode = MenuMode.Main
            pygame.display.update()
                    
    def show(self):
        self.loop()
        return self.__play

    def exit_settings(self, save:bool=False):
        
        #TODO
        if save: pass

        self.__mode = MenuMode.Main

    def settings(self):
        self.__mode = MenuMode.Settings

    def play(self):
        self.__play = True
        self.__active = False

    def exit(self):
        self.__active = False

    def __init__(self, dsp:Display):
        settings = visual_settings.GetInst()
        sz = dsp.get_size()
        
        self.__play = False
        self.__mode = MenuMode.Main
        self.__display = dsp
        self.__active = True
        self.__menu = Menu(None, (0, 0), dsp.get_size())
        self.__menu_btns = []
        self.__settings_btns = []

        self.__title = Label(self.__menu, 
                             (sz[0]/2, sz[1]/3),
                             'Silver Wind')

        self.__menu_btns.extend([
            Button(self.__menu, 
                   (sz[0]/6, 2*sz[1]/3), (200, 80), 
                   'Quit', lambda: self.exit()),

            Button(self.__menu, 
                   (sz[0]/2, 2*sz[1]/3), (200, 80), 
                   'Play', lambda: self.play()),

            Button(self.__menu, 
                   (5*sz[0]/6, 2*sz[1]/3), (200, 80), 
                   'Settings', lambda: self.settings())
        ])

        self.__settings_btns.extend([
            Button(self.__menu, 
                   (sz[0]/4, sz[1]-80), (200, 80), 
                   'Save', lambda: self.exit_settings(True)),

            Button(self.__menu, 
                   (3*sz[0]/4, sz[1]-80), (200, 80), 
                   'Exit', lambda: self.exit_settings()),
        ])



