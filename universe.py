""" Module for defining the road in the game """

import pygame

import res
from graph import Graph
import star
import file_utils

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
        self.scale = max(0.4, min(self.scale + amount * 0.1 * self.scale, 10.0))

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

        hovered_node = None
        hovered_edge = None

        for [id, vertex] in self.graph.vertex_list.items():
            current_star: star.Star = vertex.value

            if current_star:
                star_coords = ( (current_star.coordinates.x + delta_x) * self.scale , (current_star.coordinates.y + delta_y) * self.scale )
                star_radius = max(1, int(current_star.radius * 10 * self.scale))

                pygame.draw.circle(screen, star.get_constellation_color(current_star), star_coords, star_radius)

                if current_star.hypergiant:
                    pygame.draw.circle(screen, (255, 180, 0), star_coords, star_radius + 5, 2)

                for [neighbor_id, (distance, locked)] in vertex.get_connections().items():
                    neighbor_vertex = self.graph.get_vertex(neighbor_id)
                    neighbor: star.Star = neighbor_vertex.value

                    if neighbor:
                        neighbor_coords = ( (neighbor.coordinates.x + delta_x) * self.scale , (neighbor.coordinates.y + delta_y) * self.scale )

                        middle_point = ( (star_coords[0] + neighbor_coords[0]) / 2, (star_coords[1] + neighbor_coords[1]) / 2 )

                        pygame.draw.line(screen, (85, 85, 85), star_coords, neighbor_coords, 1)

                        if locked:
                            pygame.draw.line(screen, (255, 60, 60), star_coords, neighbor_coords, 3)
                        
                        BG_COLOR = (0, 0, 0) if not locked else (50, 0, 0)
                        text_image = res.Font.NJ.value.render(f"{distance}", False, (255, 255, 255), BG_COLOR)
                        screen.blit(text_image, ( (star_coords[0] + neighbor_coords[0] - text_image.get_size()[0]) / 2, (star_coords[1] + neighbor_coords[1] - text_image.get_size()[1]) / 2 ))

                        if pygame.Rect(middle_point[0] - star_radius, middle_point[1] - star_radius, star_radius * 2, star_radius * 2).collidepoint(pygame.mouse.get_pos()):
                            hovered_edge = (current_star.id, neighbor.id)
                            pygame.draw.circle(screen, (255, 0, 255), middle_point, max(10, self.scale * 10) + 5, 2)

                if pygame.Rect(star_coords[0] - star_radius, star_coords[1] - star_radius, star_radius * 2, star_radius * 2).collidepoint(pygame.mouse.get_pos()):
                    hovered_node = current_star
                    pygame.draw.circle(screen, (255, 0, 255), star_coords, star_radius + 5, 2)

        return (hovered_node, hovered_edge)
