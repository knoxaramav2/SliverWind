

import pygame
from actor import Actor

from display import Display
from playable import Player
from ui_controls import *


class GameView:

    __display       : Display
    __active        : True
    __paused        : False
    __actors        : list[Actor]
    __player        : Player

    def on_key_down(self, key):
        match key:
            case pygame.K_ESCAPE: 
                self.__paused = not self.__paused
                pygame.event.clear()
            case _:#Player handled
                return True
        return False

    def update_user_keys(self):
        keys = pygame.key.get_pressed()
        self.__player.handle_key(keys)

    def handle_events(self):
        self.update_user_keys()

        for e in pygame.event.get():
            match e.type:
                case pygame.KEYDOWN:
                    self.on_key_down(e.key)

    def handle_menu_events(self):
        pass

    def draw_actors(self):
        self.__player.draw(self.__display)

    def render_game(self):
        self.__display.screen().fill((52, 153, 77))
        self.handle_events()
        self.draw_actors()

    def render_menu(self):
        self.__display.screen().fill((32, 58, 71))
        self.handle_menu_events()

    def loop(self):
        while self.__active:
            if self.__paused:
                self.render_menu()
            else: 
                self.render_game()
            pygame.display.update()

    def show(self):
        self.loop()

    def load_map(self):
        pass

    def __init__(self, dsp:Display) -> None:
        self.__display = dsp
        self.__active = True
        self.__paused = False
        self.__player = Player()
        self.__actors = []
        