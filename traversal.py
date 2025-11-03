""" Module for defining the road in the game """

import time
import pygame

from typing import List
from graph import Graph, Vertex
from star import Star

import res

class Traversal():
    def __init__(self, graph, stats):
        """ 
        Universe constructor
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
        """
        self.base_graph: Graph = graph
        self.stats = stats
        self.nodes = []
        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.origin: Star = None
        self.use_grass = True
        self.use_investigative_labors = True
        self.playing = False
        self.current_playing_anim_vertex = 0
        self.last_epoch = 0
        self.donkey_pos = (0, 0)
        self.death_at_end = True
    
    def play(self):
        self.playing = True
        self.last_epoch = time.time()
        self.current_playing_anim_vertex = 0

    def stop(self):
        self.playing = False
        self.current_playing_anim_vertex = 0

    def get_origin_coords(self):
        if not self.playing and len(self.nodes) > 0:
            if (self.origin):
                delta_x = (self.x) * self.scale
                delta_y = (- self.y) * self.scale

                return ( (self.origin.coordinates.x + delta_x) * self.scale , (self.origin.coordinates.y + delta_y) * self.scale )
            return None
        elif len(self.nodes) > 0:
            delta_x = (self.x) * self.scale
            delta_y = (- self.y) * self.scale

            return ( (self.base_graph.get_vertex(self.nodes[self.current_playing_anim_vertex]).value.coordinates.x + delta_x) * self.scale , (self.base_graph.get_vertex(self.nodes[self.current_playing_anim_vertex]).value.coordinates.y + delta_y) * self.scale )
        return None
    
    def update(self, universe):
        self.x = universe.x
        self.y = universe.y
        self.scale = universe.scale
        self.base_graph: Graph = universe.graph

        oc = self.get_origin_coords()
        if oc:
            self.donkey_pos = ( (self.donkey_pos[0] + oc[0]) * 0.5, (self.donkey_pos[1] + oc[1]) * 0.5 )
        
        if self.playing:
            if time.time() - self.last_epoch >= 1:
                if self.current_playing_anim_vertex < len(self.nodes) - 1:
                    self.last_epoch = time.time()
                    self.current_playing_anim_vertex += 1
                    res.Sound.HIT.value.play()
                else:
                    if self.death_at_end:
                        res.Sound.DEATH.value.play()
                    self.stop()

    def set_origin(self, star: Star):
        self.origin = star
        oc = self.get_origin_coords()
        if oc:
            self.donkey_pos = oc
        self.calculate()
    
    def draw(self, screen: pygame.Surface):
        """
        Draw the universe to a surface
        Args:
            screen (pygame.Surface): The surface to draw the universe on
        """
        if self.origin is None:
            return
        
        delta_x = (self.x) * self.scale
        delta_y = (- self.y) * self.scale

        for i in range( 0, len(self.nodes) - 1, 1 ):
            s1: Star = self.base_graph.get_vertex(self.nodes[i]).value
            s2: Star = self.base_graph.get_vertex(self.nodes[i+1]).value

            s1c = ( (s1.coordinates.x + delta_x) * self.scale , (s1.coordinates.y + delta_y) * self.scale )
            s2c = ( (s2.coordinates.x + delta_x) * self.scale , (s2.coordinates.y + delta_y) * self.scale )

            pygame.draw.line(screen, (85, 255, 85), s1c, s2c, 5)

    def draw_donkey(self, screen: pygame.Surface):
        if self.origin is None:
            return
        
        delta_x = (self.x) * self.scale
        delta_y = (- self.y) * self.scale

        donkey_coords = self.donkey_pos

        sss = max(0.1, min(1.0, self.scale - 0.5))

        scaled_image = pygame.transform.scale(res.Image.BURRO.value, (sss * res.Image.BURRO.value.get_size()[0], sss * res.Image.BURRO.value.get_size()[1]))

        donkey_coords = (self.donkey_pos[0] - scaled_image.get_size()[0] / 2, self.donkey_pos[1] - scaled_image.get_size()[1])

        pygame.draw.ellipse(screen, res.Color.BACKGROUND.value, (donkey_coords[0] + scaled_image.get_size()[0] / 2 - 40*sss, donkey_coords[1] + scaled_image.get_size()[1] - 10*sss, 40*sss, 15*sss ))

        screen.blit(scaled_image, (donkey_coords[0], donkey_coords[1]))
    
    def calculate(self) -> List[int]:
        """
        Use bellman ford and pray.
        """
        if self.origin is None:
            return
        

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

        it = 0
        self.nodes = []

        while it < 300:
            it += 1
            v_id = max_route[0]
            v_from = max_route[1][1]

            self.nodes.append(v_id)

            if v_id == v_from:
                break
            else:
                max_route = (v_from, weights[v_from])
        
        self.nodes = self.nodes[::-1]

        print(self.nodes)