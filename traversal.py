""" Module for defining the road in the game """

import os
import subprocess
import copy
import time
import pygame

from typing import List
from graph import Graph, Vertex
from star import Star
from universe import Stats

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
        self.stat_lookup: dict[int, Stats] = {}
        self.x = 0
        self.y = 0
        self.scale = 1.0
        self.origin: Star = None
        self.use_only_initial = True
        self.use_investigative_labors = True
        self.playing = False
        self.current_playing_anim_vertex = 0
        self.last_epoch = 0
        self.donkey_pos = (0, 0)
        self.death_at_end = True
        self.current_stats = {}
    
    def play(self):
        if self.origin and len(self.nodes) > 0:
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
            self.current_stats = self.stat_lookup[ self.nodes[ self.current_playing_anim_vertex ]]
        else:
            self.current_stats = self.stats

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
        Priorizes paths by maximum longitude and then minimum cost
        """

        if self.origin is None:
            self.nodes = []
            self.stat_lookup = {}
            self.death_at_end = False
            return
        
        route: List[int] = [self.origin.id]
        route_cost: Stats = copy.deepcopy(self.stats)
        is_deadly = False

        it_guard = 0

        stat_lookup: dict[int, Stats] = {}
        
        def compute_next_route(
                visited_nodes: List[int],
                current_cost: Stats,
                sts: dict[int, Stats]
        ):
            nonlocal it_guard, route, route_cost, is_deadly, stat_lookup
            """ Guard for no blocking my entire desktop 🚬 """
            it_guard += 1
            if it_guard > 10000:
                exit(-1)
            """ Get current star id """
            current_star_id = visited_nodes[ len(visited_nodes) - 1 ]
            current_star = self.base_graph.get_vertex(current_star_id)
            """ Add local costs """
            current_cost.add_out_star(current_star.value, self.use_only_initial)
            """ Register current stats """
            sts[current_star_id] = current_cost
            """ Do replacement """
            if len(visited_nodes) > len(route) or ( len(visited_nodes) == len(route) and current_cost < route_cost ):
                route = visited_nodes
                route_cost = current_cost
                is_deadly = current_cost.is_deadly()
                stat_lookup = sts
            
            if current_cost.is_deadly():
                return
            
            could_travel_more = False
            traveled_more = False
            """ Search more expansion """
            for neighbor_star_id, (neighbor_star_distance, neighbor_star_locked) in current_star.adjacent.items():
                """ 
                If any longer path is found, it'll be later by other branch
                This prevents infinite loops (Python hard locks linux btw)
                """
                if neighbor_star_id in visited_nodes or neighbor_star_locked:
                    continue
                else:
                    could_travel_more = True
                    # Search for more routes
                    next_visited_nodes = copy.deepcopy(visited_nodes) + [neighbor_star_id]
                    """ Calculate travel cost """
                    next_cost = copy.deepcopy(current_cost)
                    next_cost.add_dst(neighbor_star_distance, self.use_only_initial)
                    """ Hop """
                    if next_cost.is_deadly():
                        continue
                    traveled_more = True
                    compute_next_route(next_visited_nodes, next_cost, copy.deepcopy(sts))
            """ If the thing had routes, but could not travel, it died here """
            if could_travel_more and not traveled_more:
                is_deadly = True
    
        compute_next_route(copy.deepcopy(route), copy.deepcopy(route_cost), copy.deepcopy(stat_lookup))

        self.nodes = route
        self.death_at_end = is_deadly
        self.stat_lookup = stat_lookup
    
    def open_file_in_default_editor(self, filepath):
        """
        Opens a file in the user's default text editor.
        """
        if os.name == 'nt':  # For Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # For macOS and Linux
            try:
                subprocess.run(['xdg-open', filepath]) # Linux
            except FileNotFoundError:
                try:
                    subprocess.run(['open', filepath]) # macOS
                except FileNotFoundError:
                    print(f"Could not open {filepath} with default editor.")
        else:
            print(f"Unsupported operating system: {os.name}")
    
    def generate_report(self):
        if self.origin == None or len(self.nodes) == 0:
            return
        
        with open("log.txt", "w") as log:
            log.write("Generated travel report\n")
            log.write("-------------------------------\n")
            log.write(f"Initial: {self.stats}\n")
            log.write("-------------------------------\n")
            for id in self.nodes:
                star: Star = self.base_graph.get_vertex(id).value
                stats: Stats = self.stat_lookup[ id ]
                print(stats.meta)
                log.write(f"Visited {star.name}, arrived with {stats.meta["arriveYears"]} years.\n")
                log.write(f"Spent on stay {star.timeToEat * 2} years, ate {stats.meta["kg"]}Kg of grass.\n")
                log.write(f"After staying: {stats}\n")
                log.write("----\n")
            if self.death_at_end and not "died" in stats.meta:
                log.write("Died: while traveling\n")
            elif self.death_at_end:
                log.write(f"Died: {stats.meta["died"]}\n")
            log.write("===============================\n")
            log.write("End of travel\n")
        
        self.open_file_in_default_editor("log.txt")
            