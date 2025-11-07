""" Module for defining the road in the game """

import pygame

import json

import res
from graph import Graph
from star import Star, get_constellation_color

class Stats():
    burroenergiaInicial: float = 100
    pasto: int = 300
    startAge: int = 12
    deathAge: int = 3567

    def __init__(self):
        meta = {}

    def __repr__(self):
        return f"{ min(self.startAge, self.deathAge) } of { self.deathAge } years -- { min(100, max(0, round(self.burroenergiaInicial, 2))) }% energy -- { max(0, self.pasto) }Kg grass"
    
    @staticmethod
    def get_eating_kg_per_year():
        return 1
    
    @staticmethod
    def get_health_from_energy(energy):
        k = energy / 25
        if k <= 0:
            return "muerto"
        elif k <= 1:
            return "moribundo"
        elif k <= 2:
            return "mala"
        elif k <= 3:
            return "buena"
        else:
            return "excelente"
    
    @staticmethod
    def eating_energy_intake_from_health(health):
        if health == "excelente":
            return 7
        if health == "buena":
            return 5
        if health == "mala":
            return 3
        if health == "moribundo":
            return 2
        else:
            return 0
    
    def add_dst(self, next_distance: float, use_only_initial: bool):
        self.startAge += next_distance
    
    def add_out_star(self, out_star: Star, use_only_initial: bool):
        self.meta = {}

        shouldEat = self.burroenergiaInicial < 50
        timeEating = out_star.timeToEat if shouldEat else 0
        timeAct = out_star.timeToEat if shouldEat else out_star.timeToEat * 2

        self.meta["arriveYears"] = self.startAge
        self.meta["ateTime"] = timeEating
        self.meta["invTime"] = timeAct

        self.startAge += timeEating

        """ If not died while eating grass, calculate the gained stats """
        if self.is_deadly():
            self.meta["died"] = "while eating"
            return
        else:
            consumedKg = int( timeEating * Stats.get_eating_kg_per_year() )
            self.meta["kg"] = consumedKg
            for _ in range(consumedKg):
                self.pasto -= 1
                self.burroenergiaInicial += Stats.eating_energy_intake_from_health( Stats.get_health_from_energy( self.burroenergiaInicial ) )
        
        if use_only_initial:
            """ Continue if not died after investigating (Losses not included) """
            self.startAge += timeAct
            if self.is_deadly():
                self.meta["died"] = "while investigating"
        elif len(out_star.activities) > 0:
            """ Continue if not died after investigating (Losses included) """
            timePerActivity = timeAct / len(out_star.activities)
            for act in out_star.activities:
                # Add energy loss
                self.burroenergiaInicial -= act[1] * timePerActivity
                # Add year loss
                self.startAge += act[2]
                if self.is_deadly():
                    self.meta["died"] = f"while investigating: {act[0]}"
            pass
        pass

    def get_death_causes(self):
        causes = []
        if self.deathAge < self.startAge:
            causes.append("natural_death")
        if self.burroenergiaInicial <= 0:
            causes.append("energy_loss")
        if self.pasto <= 0:
            causes.append("starvation")
        return causes

    def is_deadly(self):
        return len(self.get_death_causes()) > 0

    def __lt__(self, other):
        if isinstance(other, Stats):
            td = self.is_deadly()
            od = other.is_deadly()

            if not td and od:
                return True
            elif td and not od:
                return False
            # Compare based on sum of coordinates
            improves_age = self.startAge < other.startAge
            improves_energy = self.burroenergiaInicial < other.burroenergiaInicial
            return improves_age

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
    
    def graph_from_file(self, file_path: str) -> Stats:
        """
        Load from a JSON file.
        Args:
            file_path (str): Path to the JSON file.
        """
        stats = Stats()
        self.graph = Graph()

        with open(file_path, 'r') as file:
            data = json.load(file)

            stats.burroenergiaInicial = data["burroenergiaInicial"]
            stats.pasto = data["pasto"]
            stats.startAge = data["startAge"]
            stats.deathAge = data["deathAge"]

            # first load star data
            for constellation_data in data["constellations"]:
                for star_data in constellation_data["stars"]:
                    # handle multiple owner constellations
                    redundant_star = self.graph.get_vertex(star_data["id"])
                    if redundant_star != None:
                        # just add the constellation to the existing star if not already present
                        if constellation_data["name"] not in redundant_star.value.constellations:
                            redundant_star.value.constellations.append(constellation_data["name"])
                        for act in star_data.get("activities", []):
                            if type(act) == list and len(act) == 3 and type(act[0]) == str and type(act[1]) in [int, float] and type(act[2]) in [int, float]:
                                activity = (act[0], act[1], act[2])
                                if not activity in redundant_star.value.activities:
                                    redundant_star.value.activities.append( activity )
                        continue

                    new_star = Star(star_data["id"])

                    new_star.constellations.append(constellation_data["name"])

                    new_star.name = star_data.get("label", "unknown")
                    new_star.radius = star_data.get("radius", 0.4)
                    new_star.hypergiant = star_data.get("hypergiant", False)
                    new_star.timeToEat = star_data.get("timeToEat", 3)
                    new_star.amountOfEnergy = star_data.get("amountOfEnergy", 1)
                    coordenates = star_data.get("coordenates", {"x": 0, "y": 0})
                    new_star.coordinates = pygame.math.Vector2(
                        coordenates.get("x", 0),
                        coordenates.get("y", 0)
                    )
                    for act in star_data.get("activities", []):
                        if type(act) == list and len(act) == 3 and type(act[0]) == str and type(act[1]) in [int, float] and type(act[2]) in [int, float]:
                            activity = (act[0], act[1], act[2])
                            new_star.activities.append( activity )
                    self.graph.add_vertex(new_star.id, new_star)
            
            # then load edges
            for constellation_data in data["constellations"]:
                for star_data in constellation_data["stars"]:
                    for connection in star_data.get("linkedTo", []):
                        if self.graph.get_vertex(connection.get("starId", 0)) == None:
                            print(f"Warning: Star ID {connection.get('starId', 0)} not found in vertex list.")
                            continue
                        self.graph.add_edge(star_data["id"], connection.get("starId", 0), connection.get("distance", 0))

        return stats
    
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
            current_star: Star = vertex.value

            if current_star:
                star_coords = ( (current_star.coordinates.x + delta_x) * self.scale , (current_star.coordinates.y + delta_y) * self.scale )
                star_radius = max(1, int(current_star.radius * 10 * self.scale))

                pygame.draw.circle(screen, get_constellation_color(current_star), star_coords, star_radius)

                if current_star.hypergiant:
                    pygame.draw.circle(screen, (255, 180, 0), star_coords, star_radius + 5, 2)

                for [neighbor_id, (distance, locked)] in vertex.get_connections().items():
                    neighbor_vertex = self.graph.get_vertex(neighbor_id)
                    neighbor: Star = neighbor_vertex.value

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
