

import pygame
from actor import ACTOR_CLASS, Actor, ActorFactory
from config import Config, get_config
from controls import Button, Menu
from game_state import GameState, get_gamestate
from interface import RUN_RESULT, Runnable
from window import Window, get_win
from world_data import WorldData


class GameLoop(Runnable):

    __win           : Window
    __gstate        : GameState
    __world         : WorldData
    __active        : bool = True
    __exit_code     : RUN_RESULT = RUN_RESULT.OK
    __player        : Actor = None
    __factory       : ActorFactory
    __clock         : pygame.time.Clock
    __cfg           : Config

    __menu          : Menu

    def __update(self):
        self.__player.update()

    def __handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            match e.key:
                case pygame.K_ESCAPE:
                    if not self.__menu._visible: self.__menu.show()
                    else: self.__menu.hide()
        pass

    def __init_menu(self):
        sz = pygame.display.get_window_size()
        
        ctrls = []

        cancel = Button(
            self.__win.get_canvas(),
            'Cancel',
            callback=lambda:print('TEST QUIT')
        )

        ok = Button(
            self.__win.get_canvas(),
            'OK',
            callback=lambda:print('TEST ACCEPT')
        )
        
        self.__menu = Menu(
            self.__win.get_canvas(),
            'Menu',
            dim=(sz[0]/2, sz[1]/2)
            )
        self.__menu.add(cancel, 0, 0)
        self.__menu.add(ok, 1, 0)
        self.__menu.pack()

    def __handle_keys(self):
        keys = pygame.key.get_pressed()

        x_dir = keys[pygame.K_d] - keys[pygame.K_a]
        y_dir = keys[pygame.K_s] - keys[pygame.K_w]

        self.__player.move(x_dir, y_dir)
        
        if x_dir != 0 or y_dir != 0:
            print(f'MOVE: {self.__player.pos}')

    def __loop(self):
        while self.__active:
            self.__clock.tick(self.__cfg.fps)
            pygame.time.Clock().tick(24)
            for e in pygame.event.get():
                self.__handle_event(e)
            self.__handle_keys()
            self.__update()
            self.__draw_background()
            self.__draw_sprites()
            self.__draw_menus()
            pygame.display.update()

    def __draw_background(self):
        self.__win.draw_map(self.__world.get_current())

    def __draw_menus(self):
        self.__menu.update()

    def __draw_sprites(self):
        self.__win.draw_sprite(self.__player.sprite, self.__player.pos)
        self.__win.render()

    def __spawn_player(self):
        self.__player = self.__factory.Create(
            ACTOR_CLASS.PLAYER, False,
            'dev', (5, 5), 
        )
        pass

    def run(self) -> RUN_RESULT:
        self.__clock = pygame.time.Clock()
        map = self.__world.get_current()
        self.__win.draw_map(map)
        self.__spawn_player()
        self.__loop()
        return self.__exit_code
    
    def exit(self):
        self.__active = False

    def __init__(self):
        super().__init__()
        self.__cfg = get_config()
        self.__win = get_win()
        self.__gstate = get_gamestate()
        self.__world = self.__gstate.get_worlddata()
        self.__factory = ActorFactory()
        self.__init_menu()
