import pygame
from enum import Enum

class Color(Enum):
    """ Preloaded colors """
    BACKGROUND = (0, 0, 25)

class Font(Enum):
    """ Preloaded fonts """
    NJ = pygame.font.Font("font/NJ-display.ttf", 24)

class Image(Enum):
    """ Preloaded textures """
    BURRO = pygame.transform.scale( pygame.image.load("img/burro.png").convert_alpha(), (90, 80) )