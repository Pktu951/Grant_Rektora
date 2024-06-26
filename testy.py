import numpy as np
import math

class LidarMap:
    def __init__(self, map_data):
        self.map = map_data

class RoadFinder:
    def __init__(self, map_class: LidarMap, starting_point: tuple, ending_point: tuple, car_length=1.5, car_width=0.5):
        if not hasattr(map_class, 'map'):
            raise ValueError("LidarMap class must have a 'map' attribute")
        self.lidar_map = map_class.map
        self.car_length = car_length
        self.car_width = car_width
        self.starting_point = starting_point
        self.ending_point = ending_point
        self.path = []

    def __is_path_clear(self, start, dx, dy):
        x, y = start
        nx, ny = x + dx, y + dy
        if not (0 <= nx < len(self.lidar_map) and 0 <= ny < len(self.lidar_map[0])):
            return False
        return self.lidar_map[nx][ny] == 0


    def __create_graph(self):
        keys = [(i, j) for i, row in enumerate(self.lidar_map) for j, val in enumerate(row) if not val]
        if not keys:
            raise ValueError("No valid path in the lidar map")
        key_to_index = {key: idx for idx, key in enumerate(keys)}
        graph = {i: [] for i in range(len(keys))}
        edge_weights = {}

        for idx, (x, y) in enumerate(keys):
            neighbors = [
                (-1, 0), (1, 0), (0, -1), (0, 1),  
                (-1, -1), (-1, 1), (1, -1), (1, 1)  
            ]
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if (nx, ny) in key_to_index and self.__is_path_clear((x, y), dx, dy):
                    neighbor_index = key_to_index[(nx, ny)]
                    graph[idx].append(neighbor_index)
                    if abs(dx) + abs(dy) == 1:  
                        edge_weights[(idx, neighbor_index)] = 1
                    else:  # diagonal move
                        edge_weights[(idx, neighbor_index)] = math.sqrt(2)

        print("Graph:", graph)
        print("Keys:", keys)
        print("Edge Weights:", edge_weights)

        return graph, keys, edge_weights


    def __relax_edges(self, graph, edge_weights, distances, predecessor):
        num_vertices = len(graph)
        for _ in range(num_vertices - 1):
            for u in range(num_vertices):
                for v in graph[u]:
                    weight = edge_weights[(u, v)]
                    if distances[v] > distances[u] + weight:
                        distances[v] = distances[u] + weight
                        predecessor[v] = u

        # Debugging prints
        print("Distances after relaxation:", distances)
        print("Predecessor after relaxation:", predecessor)

    def __reconstruct_path(self, predecessor, start_index, end_index):
        path_indices = []
        current = end_index
        while current != start_index:
            path_indices.append(current)
            current = predecessor[current]
            if current == -1:  # path not found
                return []
        path_indices.append(start_index)
        path_indices.reverse()
        return path_indices

    def __bellman_ford(self, graph, keys, edge_weights):
        if self.starting_point not in keys or self.ending_point not in keys:
            raise ValueError("Starting or ending point is not in the lidar map")
        num_vertices = len(graph)
        start_index = keys.index(self.starting_point)
        end_index = keys.index(self.ending_point)
        distances = [np.inf] * num_vertices
        predecessor = [-1] * num_vertices

        distances[start_index] = 0

        self.__relax_edges(graph, edge_weights, distances, predecessor)

        if distances[end_index] == np.inf:  # No path found
            return []
        
        path_indices = self.__reconstruct_path(predecessor, start_index, end_index)
        if not path_indices:
            return []
        self.path = [keys[idx] for idx in path_indices]

        # Debugging prints
        print("Path indices:", path_indices)
        print("Final path:", self.path)

        return self.path

    def find_path(self):
        graph, keys, edge_weights = self.__create_graph()
        return self.__bellman_ford(graph, keys, edge_weights)

    def __repr__(self):
        return "[" + " -> ".join(map(str, self.path)) + "]"

def test_road_finder():
    test_cases = [
        {
            "name": "Simple path",
            "map_data": [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0]
            ],
            "start": (0, 0),
            "end": (2, 3),
            "expected_path": [(0, 0), (0, 1), (0, 2), (1, 3), (2, 3)]
        },
        {
            "name": "Blocked path",
            "map_data": [
                [0, 0, 0],
                [0, 1, 1],
                [0, 0, 0]
            ],
            "start": (0, 0),
            "end": (2, 2),
            "expected_path": [(0, 0), (1, 0), (2, 1), (2, 2)]
        },
        {
            "name": "Diagonal path",
            "map_data": [
                [0, 1, 0],
                [0, 0, 0],
                [0, 0, 0]
            ],
            "start": (0, 0),
            "end": (2, 2),
            "expected_path": [(0, 0), (1, 1), (2, 2)]
        }
    ]

    for case in test_cases:
        print(f"Running test case: {case['name']}")
        lidar_map = LidarMap(case["map_data"])
        road_finder = RoadFinder(lidar_map, case["start"], case["end"])
        path = road_finder.find_path()
        assert path == case["expected_path"], f"Test '{case['name']}' failed: expected {case['expected_path']}, got {path}"
        print(f"Test '{case['name']}' passed!")

# Uruchomienie testów
test_road_finder()