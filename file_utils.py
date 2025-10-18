import json
import pygame
from graph import Graph
import star

def graph_from_file(file_path: str) -> Graph:
    """
    Load a graph from a JSON file.
    Args:
        file_path (str): Path to the JSON file.
    Returns:
        Graph: An instance of the Graph class populated with data from the file.
    """
    universe = Graph()
    with open(file_path, 'r') as file:
        data = json.load(file)

        # first load star data
        for constellation_data in data["constellations"]:
            for star_data in constellation_data["stars"]:
                # handle multiple owner constellations
                redundant_star = universe.get_vertex(star_data["id"])
                if redundant_star != None:
                    # just add the constellation to the existing star if not already present
                    if constellation_data["name"] not in redundant_star.value.constellations:
                        redundant_star.value.constellations.append(constellation_data["name"])
                    continue

                new_star = star.Star(star_data["id"])

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

                universe.add_vertex(new_star.id, new_star)
        
        # then load edges
        for constellation_data in data["constellations"]:
            for star_data in constellation_data["stars"]:
                for connection in star_data.get("linkedTo", []):
                    if universe.get_vertex(connection.get("starId", 0)) == None:
                        print(f"Warning: Star ID {connection.get('starId', 0)} not found in vertex list.")
                        continue
                    universe.add_edge(star_data["id"], connection.get("starId", 0), connection.get("distance", 0))

    return universe