import utils
from student_utils import *
import networkx as nx


def greedijk(num_of_locations, num_houses, list_locations, list_houses, starting_car_location, adjacency_matrix):
    G = adjacency_matrix_to_graph(adjacency_matrix)[0]
    paths = dict(nx.all_pairs_shortest_path(G))
    #list_houses = [list_locations.index(house) for house in list_houses]
    # new dict of dicts for total edge weight for each path
    paths_lengths = {i: dict() for i in range(num_of_locations)}
    for start_node in paths.keys():
        for end_node, path in paths[start_node].items():
            l = 0
            for start, end in zip(path[:-1], path[1:]):
                l += adjacency_matrix[start][end]
            paths_lengths[start_node][end_node] = l

    homes = set([list_locations.index(home) for home in list_houses])
    path = list()
    
    # greedily take the path to the closest home
    # add starting location
    start = list_locations.index(starting_car_location)
    path.append(start)
    # remove starting location from homes if it is one
    if start in homes:
        homes.remove(start)
    
    # iteratively find the closest home that has yet to be gone to,
    # add it to the path and remove it from homes needed to go to
    curr = start
    while homes:
        paths_lengths_curr = paths_lengths[curr]
        closest = min(homes, key=lambda home: paths_lengths_curr[home])
        path.extend(paths[curr][closest][1:])
        homes.remove(closest)
        curr = path[-1]

    # go back to the start
    path.extend(paths[curr][start][1:])

    return path, paths, paths_lengths
