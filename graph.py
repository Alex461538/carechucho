import pygame

class Vertex:
    """A vertex in a graph.
    """
    def __init__(self, id):
        self.id = id
        self.value: any = None
        self.adjacent = {}

    def add_neighbor(self, neighbor, weight=0):
        """Add a neighbor to this vertex."""
        self.adjacent[neighbor] = (weight, False)

    def get_connections(self):
        """Get all neighbors of this vertex."""
        return self.adjacent

    def get_id(self):
        """Get the id of this vertex."""
        return self.id

class Graph:
    def __init__(self):
        self.vertex_list = {}
        self.num_vertex = 0
    
    def lock_edge(self, from_id, to_id, value=None):
        """Lock an edge between two vertices."""
        if from_id in self.vertex_list and to_id in self.vertex_list:
            if to_id in self.vertex_list[from_id].adjacent:
                weight, l = self.vertex_list[from_id].adjacent[to_id]
                self.vertex_list[from_id].adjacent[to_id] = (weight, value if value is not None else not l)
            if from_id in self.vertex_list[to_id].adjacent:
                weight, l = self.vertex_list[to_id].adjacent[from_id]
                self.vertex_list[to_id].adjacent[from_id] = (weight, value if value is not None else not l)

    def add_vertex(self, id, value = None):
        """Add a vertex to the graph."""
        self.num_vertex += 1
        new_vertex = Vertex(id)
        new_vertex.value = value
        self.vertex_list[id] = new_vertex
        return new_vertex

    def get_vertex(self, id):
        """Get a vertex by id."""
        return self.vertex_list.get(id)

    def add_edge(self, from_id, to_id, weight=0):
        """Add an edge to the graph."""
        if from_id not in self.vertex_list:
            self.add_vertex(from_id)
        if to_id not in self.vertex_list:
            self.add_vertex(to_id)

        self.vertex_list[from_id].add_neighbor(to_id, weight)
        self.vertex_list[to_id].add_neighbor(from_id, weight)

    def get_vertices(self):
        """Get all vertex ids in the graph."""
        return self.vertex_list.keys()