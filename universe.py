""" Module for defining the road in the game """

import pygame

from graph import Graph
import star
import file_utils

NJ = pygame.font.Font("font/credits-small.ttf", 24)

class Universe():
    def __init__(self, screen_width: int = 0, screen_height: int = 0):
        """ 
        Universe constructor
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.graph = Graph()
        self.x = 0
        self.y = 0
        self.scale = 1.0
    
    def translate(self, dx: int, dy: int):
        """ Translate the universe by a given amount """
        self.x += dx / ( self.scale * self.scale )
        self.y += dy / ( self.scale * self.scale )
    
    def zoom(self, amount: int, mouse_position: pygame.math.Vector2 = pygame.math.Vector2(0,0)):
        """ Zoom the universe in or out by a given amount """
        old_scale = self.scale
        self.scale = max(0.1, min(self.scale + amount * 0.1 * self.scale, 5.0))

        pointer = pygame.math.Vector2(
            (mouse_position.x / old_scale) - self.x * old_scale,
            (mouse_position.y / old_scale) + self.y * old_scale,
        )

        new_pointer = pygame.math.Vector2(
            (mouse_position.x / self.scale) - self.x * self.scale,
            (mouse_position.y / self.scale) + self.y * self.scale
        )

        self.x += (new_pointer.x - pointer.x) * (1 / self.scale)
        self.y -= (new_pointer.y - pointer.y) * (1 / self.scale)
    
    def update(self, *args, **kwargs):
        """ Update universe's main logic """
        return
    
    def graph_from_file(self, file_path: str):
        """
        Load from a JSON file.
        Args:
            file_path (str): Path to the JSON file.
        """
        self.graph = file_utils.graph_from_file(file_path)
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the universe to a surface
        Args:
            screen (pygame.Surface): The surface to draw the universe on
        """
        delta_x = (self.x) * self.scale
        delta_y = (- self.y) * self.scale

        for [id, vertex] in self.graph.vertex_list.items():
            current_star: star.Star = vertex.value

            if current_star:
                star_coords = ( (current_star.coordinates.x + delta_x) * self.scale , (current_star.coordinates.y + delta_y) * self.scale )
                star_radius = max(1, int(current_star.radius * 10 * self.scale))

                for [neighbor_id, distance] in vertex.get_connections().items():
                    neighbor_vertex = self.graph.get_vertex(neighbor_id)
                    neighbor: star.Star = neighbor_vertex.value

                    if neighbor:
                        neighbor_coords = ( (neighbor.coordinates.x + delta_x) * self.scale , (neighbor.coordinates.y + delta_y) * self.scale )

                        pygame.draw.line(screen, (85, 85, 85), star_coords, neighbor_coords, 1)

                        text_image = NJ.render(f"{distance}", False, (255, 255, 255), (0,0,0))

                        screen.blit(
                            text_image,
                            ( (star_coords[0] + neighbor_coords[0] - text_image.get_size()[0]) / 2, (star_coords[1] + neighbor_coords[1] - text_image.get_size()[1]) / 2 ))

                pygame.draw.circle(screen, star.get_constellation_color(current_star), star_coords, star_radius)
