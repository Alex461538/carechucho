import pygame

class Star:
    def __init__(self, id):
        self.id = id
        self.name = ""
        self.radius = 1
        self.timeToEat = 1
        self.amountOfEnergy = 1
        self.coordinates = pygame.math.Vector2(0,0)
        self.hypergiant = False
        self.constellations = []

constellation_colors = {}

def get_name_color(name: str) -> tuple:
    """
    Get the color for the star's name based on its type.
    Args:
        star (Star): The star object.
    Returns:
        tuple: RGB color tuple.
    """
    if name in constellation_colors:
        return constellation_colors[name]
    bigint = hash(name)
    r = (bigint & 0xFF0000) >> 16
    g = (bigint & 0x00FF00) >> 8
    b = bigint & 0x0000FF
    color = ()
    if (r + g + b) / 3 < 128:
        color = (r + 128, g + 128, b + 128)
    color = (r, g, b)  # default white color
    constellation_colors[name] = color
    return color

def get_constellation_color(star: Star) -> tuple:
    """
    Get the color associated with a constellation.
    Args:
        constellation_name (str): Name of the constellation.
    Returns:
        tuple: RGB color tuple.
    """
    if len(star.constellations) > 1:
        return (255, 60, 60)  # for stars in multiple constellations

    return get_name_color(star.constellations[0])