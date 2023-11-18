from enum import Enum
import pygame
from display import Display
from game_view import GameView
from main_menu import MainMenu
from visual_settings import VisualSettings

GameMode = Enum(
    'Mode', [
        'MainMenu',
        'Movie',
        'Game',
        'Exit'
    ]
)

class GameController:

    __display   : Display
    __mode      : GameMode

    __menu      : MainMenu
    __game      : GameView
    
    def loop(self):
        while self.__mode != GameMode.Exit:
            match self.__mode:
                case GameMode.Game: 
                    self.__game.show()
                case GameMode.MainMenu: 
                    if self.__menu.show(): self.__mode = GameMode.Game
                    else: self.__mode = GameMode.Exit
                case GameMode.Movie: pass

    def start(self):
        self.loop()

    def __init__(self, dsp:Display):
        self.__display = dsp
        self.__game = GameView(dsp)
        self.__menu = MainMenu(dsp)
        self.__mode = GameMode.MainMenu


