""" Module for defining the road in the game """

import pygame

import res
from graph import Graph
import star
import file_utils

from universe import Universe

class Traversal():
    def __init__(self, graph):
        """ 
        Universe constructor
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.base_graph = graph
        self.graph = graph
        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.origin = None
    
    def follow_universe(self, universe: Universe):
        self.x = universe.x
        self.y = universe.y
        self.scale = universe.scale
    
    def update(self, *args, **kwargs):
        """ Update universe's main logic """
        return

    def set_origin(self, star: star.Star):
        self.origin = star
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the universe to a surface
        Args:
            screen (pygame.Surface): The surface to draw the universe on
        """
        if self.graph is None or self.origin is None:
            return
        
        delta_x = (self.x) * self.scale
        delta_y = (- self.y) * self.scale

        for [id, vertex] in self.graph.vertex_list.items():
            current_star: star.Star = vertex.value

            if current_star:
                star_coords = ( (current_star.coordinates.x + delta_x) * self.scale , (current_star.coordinates.y + delta_y) * self.scale )
                star_radius = max(1, int(current_star.radius * 10 * self.scale))

                if current_star == self.origin:
                    pygame.draw.circle(screen, (255, 180, 255), star_coords, star_radius + 10, 2)

                for [neighbor_id, distance] in vertex.get_connections().items():
                    neighbor_vertex = self.graph.get_vertex(neighbor_id)
                    neighbor: star.Star = neighbor_vertex.value

                    if neighbor:
                        neighbor_coords = ( (neighbor.coordinates.x + delta_x) * self.scale , (neighbor.coordinates.y + delta_y) * self.scale )
                        pygame.draw.line(screen, (85, 255, 85), star_coords, neighbor_coords, 5)

    def draw_donkey(self, screen: pygame.Surface):
        if self.graph is None or self.origin is None:
            return
        
        delta_x = (self.x) * self.scale
        delta_y = (- self.y) * self.scale

        origin_coords = ( (self.origin.coordinates.x + delta_x) * self.scale , (self.origin.coordinates.y + delta_y) * self.scale )

        sss = max(0.1, min(1.0, self.scale - 0.5))

        scaled_image = pygame.transform.scale(res.Image.BURRO.value, (sss * res.Image.BURRO.value.get_size()[0], sss * res.Image.BURRO.value.get_size()[1]))

        origin_coords = ( origin_coords[0] - scaled_image.get_size()[0] / 2 + 16, origin_coords[1] - scaled_image.get_size()[1] )

        pygame.draw.ellipse(screen, res.Color.BACKGROUND.value, (origin_coords[0] + scaled_image.get_size()[0] / 2 - 40*sss, origin_coords[1] + scaled_image.get_size()[1] - 10*sss, 40*sss, 15*sss ))

        screen.blit(scaled_image, (origin_coords[0], origin_coords[1]))