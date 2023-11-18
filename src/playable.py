

import pygame
from actor import Actor


class Player(Actor):

    def handle_key(self, keys):

        dx = 0
        dy = 0

        if keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_RIGHT]: dx += 1
        
        self.move(dx, dy)

    def __init__(self) -> None:
        super().__init__()
        
        self.clr = pygame.Color(255, 0, 0)
        self.speed = 1.0
        self.speed_mult = 1.0


