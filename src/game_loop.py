

import pygame
from actor import ACTOR_CLASS, Actor, ActorFactory
from config import Config, get_config
from controls import Button, Menu
from game_state import GameState, get_gamestate
from interface import RUN_RESULT, Runnable
from overworld import Overworld
from util import GetUtil, Util
from window import Camera, Window, get_win
from world_data import Map, WorldData


class GameLoop(Runnable):

    __win           : Window
    __cam           : Camera
    __gstate        : GameState
    __world         : WorldData
    __overworld     : Overworld
    __active        : bool = True
    __pause         : bool = False
    __exit_code     : RUN_RESULT = RUN_RESULT.OK
    __player        : Actor = None
    __factory       : ActorFactory
    __clock         : pygame.time.Clock
    __cfg           : Config
    __util          : Util

    __menu          : Menu


#Events
    def __update(self):
        self.__player.update()

    def __handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            match e.key:
                case pygame.K_ESCAPE:
                    if not self.__menu._visible: 
                        self.__menu.show()
                        self.__pause = True
    
    def __handle_keys(self):
        keys = pygame.key.get_pressed()

        x_dir = keys[pygame.K_d] - keys[pygame.K_a]
        y_dir = keys[pygame.K_s] - keys[pygame.K_w]
        sprint = keys[pygame.K_LSHIFT]

        if x_dir == 0 and y_dir == 0: return

        x_dir += sprint*x_dir 
        y_dir += sprint*y_dir
        self.__player.move(x_dir, y_dir)
        self.__cam.move(self.__player.pos)

        ppos = self.__player.pos
        cpos = self.__cam.get_pos()
        print(f'{ppos[0]},{ppos[1]} : {cpos[0]},{cpos[1]}')

    def __handle_menu(self):

        for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_KP_ENTER:
                        pass
                    elif e.key == pygame.K_ESCAPE:
                        self.__menu.hide()
                        self.__pause = False
                elif e.type == pygame.MOUSEBUTTONUP:
                    self.__menu.on_click()
     
#Menu
    def __close_menu(self):
        self.__menu.hide()
        self.__pause=False

#General
    def __loop(self):
        while self.__active:
            self.__clock.tick(self.__cfg.fps)

            if self.__pause:
                self.__handle_menu()
                continue

            for e in pygame.event.get():
                self.__handle_event(e)
            self.__handle_keys()
            self.__update()
            self.__draw_background()
            self.__draw_sprites()
            self.__draw_menus()
            pygame.display.update()

    def __spawn_player(self):
        self.__player = self.__factory.Create(
            ACTOR_CLASS.PLAYER, False,
            'dev', (5, 5), 
        )
        pass

    def run(self) -> RUN_RESULT:
        self.__clock = pygame.time.Clock()
        self.__spawn_player()
        self.__loop()
        return self.__exit_code
    
    def exit(self):
        self.__active = False

    def __load_island(self):
        self.__cam.fade_out()
        self.__overworld = Overworld(self.__world)
        #load graphic
        self.__cam.fade_in()

#Rendering
    def __draw_sprites(self):
        self.__win.draw_sprite(self.__player.sprite, self.__player.pos)
        self.__win.render()

    def __draw_background(self):
        self.__win.clear_screen()
        self.__win.draw_island(self.__overworld)

    def __draw_menus(self):
        self.__menu.update()

#Inits
    def __init_menu(self):
        sz = pygame.display.get_window_size()
        
        self.__menu = Menu(
            self.__win.get_canvas(),
            'Menu',
            dim=(sz[0]/2, sz[1]/2)
            )
        
        cancel = Button(
            self.__win.get_canvas(),
            'Cancel',
            callback=self.__close_menu
        )

        ok = Button(
            self.__win.get_canvas(),
            'OK',
            callback=self.__close_menu
        )
        
        self.__menu.add(cancel, 0, 0)
        self.__menu.add(ok, 1, 0)
        self.__menu.pack()

    def __init_camera(self):
        self.__cam = self.__win.get_camera()

    def __init__(self):
        super().__init__()
        self.__cfg = get_config()
        self.__util = GetUtil()
        self.__win = get_win()
        self.__gstate = get_gamestate()
        self.__world = self.__gstate.get_worlddata()
        self.__factory = ActorFactory()
        self.__init_menu()
        self.__init_camera()

        self.__load_island()
