import random
import numpy as np
from numpy.random import binomial
from numpy.linalg import norm
from uuid import uuid4
import networkx as nx


LIM = 1414213562.373095  # side length of 2bil diag square
EDGE_CHANCE = 0.5
DECIMALS = 5

LOCATIONS = 200
TAS = 100
FILENAME = "200.in"


def rounded_random():
    return round(random.random()*LIM, 2)

def gen_mat(n_loc: int):
    # randomly generate points in 2d space
    points = set()
    for _ in range(n_loc):
        point = (rounded_random(), rounded_random())
        # make sure point is unique
        while point in points:
            point = (rounded_random(), rounded_random())
        points.add(point)

    points = np.array(list(points))
    adjacency_dict = {i: [0]*n_loc for i in range(n_loc)}
    # each point/vertex has a list where each element corresponds to the
    # distance between the point and all other points; the edge length is
    # simply the euclidean distance to satisfy the triangle inequality
    for i, point in enumerate(points):
        # only fill the upper triangle of the matrix; the lower triangle will
        # be mirrored
        for j in range(i+1, n_loc):
            # randomly decide if the edge exists
            if binomial(1, EDGE_CHANCE):
                # euclidean distance
                # https://stackoverflow.com/a/1401828
                adjacency_dict[i][j] = round(norm(point - points[j]), DECIMALS)
    
    adjacency_matrix = np.array(list(adjacency_dict.values()))
    # mirror the upper triangle to the lower triangle
    # https://stackoverflow.com/a/58806735
    adjacency_matrix = adjacency_matrix + adjacency_matrix.T - np.diag(np.diag(adjacency_matrix))

    return points, adjacency_matrix


# reset
open(FILENAME, "w").close()

with open(FILENAME, "w") as file:
    # output line 1: number of locations
    print(LOCATIONS, file=file)

    # output line 2: number of homes
    print(TAS, file=file)

    # output line 3: list of distinct location names
    names = set()
    for _ in range(LOCATIONS):
        name = uuid4().hex[:20]
        while name in names:
            name = uuid4().hex[:20]
        names.add(name)
        print(name, file=file, end=' ')
    print(file=file)

    # output line 4: list of homes names
    names = tuple(names)
    used = set()
    for _ in range(TAS):
        name = random.choice(names)
        # TAs can't live in the same home
        while name in used:
            name = random.choice(names)
        used.add(name)
        print(name, file=file, end=' ')
    print(file=file)

    # output line 5: starting point location name
    print(random.choice(names), file=file, end='')
    print(file=file)

    # rest of output lines: adjacency matrix rep. of graph
    mat = gen_mat(LOCATIONS)[1]
    # keep generating graphs until it is connected
    while not nx.is_connected(nx.from_numpy_matrix(mat)):
        mat = gen_mat(LOCATIONS)[1]
    for l in mat:
        for num in l:
            print(num or "x", file=file, end=' ')
        print(file=file)
