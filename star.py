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
    return (255, 192, 203)