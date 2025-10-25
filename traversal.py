""" Module for defining the road in the game """

import pygame

import res
from graph import Graph, Vertex
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
        self.base_graph: Graph = graph
        self.graph: Graph = Graph()
        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.origin: star.Star = None
    
    def follow_universe(self, universe: Universe):
        self.x = universe.x
        self.y = universe.y
        self.scale = universe.scale
        self.base_graph: Graph = universe.graph
    
    def update(self, *args, **kwargs):
        """ Update universe's main logic """
        return

    def set_origin(self, star: star.Star):
        self.origin = star
        self.calculate()
    
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
            current_star: star.Star = self.base_graph.get_vertex(vertex.value).value

            if current_star:
                star_coords = ( (current_star.coordinates.x + delta_x) * self.scale , (current_star.coordinates.y + delta_y) * self.scale )
                star_radius = max(1, int(current_star.radius * 10 * self.scale))

                if current_star == self.origin:
                    pygame.draw.circle(screen, (255, 180, 255), star_coords, star_radius + 10, 2)

                for [neighbor_id, distance] in vertex.get_connections().items():
                    neighbor_vertex = self.base_graph.get_vertex(neighbor_id)
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
    
    def calculate(self):
        """
        Use bellman ford and pray.
        """
        if self.origin is None:
            return
        
        self.graph = Graph()

        # Declare the weights registry & fill it
        weights = {}
        for vertex in self.base_graph.vertex_list.items():
            if vertex[0] == self.origin.id:
                weights[ vertex[0] ] = (0, vertex[0], 0)
            else:
                weights[ vertex[0] ] = (float('inf'), -1, float("inf"))
        
        if len(weights.items()) == 0:
            return
        
        for i in range(len(weights.items())):
            improved: bool = False
            # iterate over all vertexes
            for weight_pair in weights.items():
                vertex_id = weight_pair[0]
                vertex_distance = weight_pair[1][0]
                vertex_from_id = weight_pair[1][1]
                vertex_jumps = weight_pair[1][2]
                
                #print("\tid: ", vertex_id, (vertex_distance, vertex_from_id))

                if (vertex_from_id == -1):
                    continue

                # iterate over all edeges, assume it is undirected graph
                for edge in self.base_graph.get_vertex(vertex_id).adjacent.items():
                    edge_dest_id = edge[0]
                    edge_weight = edge[1][0]
                    edge_locked = edge[1][1]

                    next_weight = vertex_distance + (float("inf") if edge_locked else edge_weight)

                    #print("\t\tedge: ", edge, next_weight)

                    if weights[edge_dest_id][0] > next_weight:
                        improved = True
                        weights[edge_dest_id] = (next_weight, vertex_id, vertex_jumps + 1)

            #print("it: ", i, weights)
            if not improved:
                break
        
        # Get longest route
        max_route = None

        for v_info in weights.items():
            if v_info[1][2] != float("inf") and ( max_route is None or v_info[1][2] > max_route[1][2] ):
                max_route = v_info

        #print(weights, max_route)
        
        while max_route != None:
            v_id = max_route[0]
            v_from = max_route[1][1]
            v_dst = max_route[1][0]

            if self.graph.get_vertex(v_id) is None:
                self.graph.add_vertex(v_id, v_id)

            if v_id != v_from:
                self.graph.add_vertex(v_from, v_from)
                self.graph.add_edge(v_from, v_id, v_dst)
                max_route = (v_from, weights[v_from])
            else:
                break