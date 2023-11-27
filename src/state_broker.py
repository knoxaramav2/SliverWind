
from enum import Enum
import os
import pathlib
import sys

import pygame
from config import Config, get_config
from game_loop import GameLoop
from interface import RUN_RESULT, Runnable
from main_ui import MainMenu
from save_manager import SaveManager, get_save_manager
from util import GetUtil, Util


BASE_STATES = Enum(
    'b_states', [
        'MAIN_MENU',
        'NEW_WORLD',
        'LOAD_WORLD',
        'MAIN_SETTINGS',
        'GAME_PROPER',
        'DEV_START',
        'EXIT'
    ]
)


class StateBroker(Runnable):

    state           : BASE_STATES = BASE_STATES.MAIN_MENU
    exit_code       : RUN_RESULT = RUN_RESULT.OK

    __cfg           : Config
    __active        : bool = True
    __save_man      : SaveManager
    __util          : Util
    
    def run(self) -> RUN_RESULT:
        self.loop()
        return self.exit_code
    
    def exit(self):
        self.__active = False

    def loop(self):
        while self.__active:
            self.handle_events()

    def handle_events(self):
        match self.state:
            case BASE_STATES.MAIN_MENU: 
                main_menu = MainMenu('SliverWind')
                res = main_menu.run()
                if res == RUN_RESULT.EXIT: self.__active = False
                else: self.state = BASE_STATES.MAIN_MENU
            case BASE_STATES.NEW_WORLD: 
                #get world file
                #create player object
                #mix into save state
                #save state
                #load from state

                self.state = BASE_STATES.GAME_PROPER
            case BASE_STATES.LOAD_WORLD: 
                #get save file
                #load save file

                self.state = BASE_STATES.GAME_PROPER
            case BASE_STATES.MAIN_SETTINGS: pass
            case BASE_STATES.GAME_PROPER:
                gameloop = GameLoop()
                res = gameloop.run()
                if res == RUN_RESULT.EXIT: self.__active = False
                elif res == RUN_RESULT.MENU: self.state = BASE_STATES.MAIN_MENU
                else: self.state = BASE_STATES.EXIT
            case BASE_STATES.DEV_START: 
                #get save file or create if not exist
                load_path = self.__cfg.dev_start_map
                save_file = self.__cfg.dev_save_file
                world_file = pathlib.Path(load_path).parts[0]
                world_file = self.__util.join(self.__util.gamedata_uri, [world_file, world_file+'.swc'])

                self.__save_man.set_target(self.__util.dev_save_name)

                if save_file == None:
                    self.__save_man.load(world_file)
                else:
                    self.__save_man.load(save_file)
                
                self.__save_man.save()

                #create god player if godmode activated
                #set active map to selected
                #save to DEV state
                #load from state



                self.state = BASE_STATES.GAME_PROPER
            case BASE_STATES.EXIT: 
                self.exit()

    def __init__(self) -> None:
        super().__init__()

        self.__cfg = get_config()
        self.__util = GetUtil()
        self.__save_man = get_save_manager()
