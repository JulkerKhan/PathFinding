from typing import Dict, List

from simanneal import Annealer

import utils
from student_utils import *
from greedijk import greedijk
import networkx as nx
import numpy as np
from collections import defaultdict
import random

class DTH(Annealer):

    def __init__(self, *, input_filename: str = None, output_filename: str = None):
        """
        state should be the cycle represented as a list like what is returned
        by the networkx shortest paths functions
        """
        self.prob = 0.9
        if input_filename:
            self.filename = input_filename
            self.input_data = utils.read_file(self.filename)
            # location to list of TA's homes such that the corresponding TA's were
            # dropped off at the location
            self.dropoff_mapping: defaultdict[int, List[int]] = defaultdict(list)
            (
                self.num_of_locations, 
                self.num_houses, 
                self.list_locations, 
                self.list_houses, 
                self.starting_car_location, 
                self.adjacency_matrix
            ) = data_parser(self.input_data)

            # nx graph
            self.g = adjacency_matrix_to_graph(self.adjacency_matrix)[0]
            self.neighbors = [list(self.g.neighbors(i)) for i in range(self.num_of_locations)]
            self.location_name_index_dict = {location: self.location_name_to_index(location) for location in self.list_locations}

            # set initial solution to greedy dijkstra's
            state, self.paths, self.paths_lengths = greedijk(
                self.num_of_locations, 
                self.num_houses, 
                self.list_locations, 
                self.list_houses, 
                self.starting_car_location, 
                self.adjacency_matrix
            )
            output_file_path = None
            if output_filename:
                try:
                    self.output_data = utils.read_file(output_filename)
                    output_file_path = [self.location_name_index_dict[location] for location in self.output_data[0]]
                except:
                    pass
            
            #r = np.random.randint(len(self.list_locations))
            #while(r == state[0]):
            #    r = random.choice(self.list_locations)
            #state = self.paths[state[0]][r] + self.paths[r][state[0]]
            #print(state)
            super().__init__(output_file_path or state)#[self.location_name_index_dict[self.starting_car_location]]*2)#state)
            #super().__init__(state)
    def set_filename(filename: str):
        self.filename = filename
        input_data = utils.read_file(filename)
        # location to list of TA's homes such that the corresponding TA's were
        # dropped off at the location
        self.dropoff_mapping: Dict[int, List[int]] = dict()
        (
            self.num_of_locations, 
            self.num_houses, 
            self.list_locations, 
            self.list_houses, 
            self.starting_car_location, 
            self.adjacency_matrix
        ) = data_parser(input_data)

    @property
    def car_cycle(self):
        return self.state

    def default(self):
        self.gen_greedy_dropoff()
        return self.state, self.dropoff_mapping

    def move(self):
        """
        possible moves:
            delete a node from the cycle
                this involves randomly choosing a node in the cycle to remove
                and then rebuilding the cycle somehow; if removing the node makes
                constructing a cycle impossible, reroll the move
            add a node to the cycle
                this involves choosing a spot in the path to insert another node
                and then perhaps simply greedily (could be random?) choosing its closest neighbor,
                inserting it after the chosen node and then find the path from
                that closest neighbor to the node that was originally to the right
                of the chosen spot
            drop a TA off at a different node
                actually this shouldn't be a move and every move should auto place
                TA's to be dropped off at the node in the cycle that is closest to
                their home

        TODO: make operations in this function as effecient as possible; e.g. don't repeat
              any work that can be stored, etc.
        TODO: add comment
        """
        if random.random() < self.prob:
            #print('del')
            self.delete_node()
        else:
            #print('add')
            self.add_node()

    def randomize(self):
        return
        #self.state = random.choice(nx.all_simple_paths(self.g, self.state[0]))
    def delete_node(self):
        newpath = self.car_cycle.copy()
        # choose random index in path to delete; not first or last because they must be the starting location
        if len(newpath) <= 2:
            return 
        dele = np.random.randint(1, len(newpath) - 1)
        old = newpath[dele]
        front = newpath[:dele]
        back = newpath[dele+1:]
        new = old
        i = 0
        while new == old and i < 3:
            new = random.choice(self.neighbors[front[-1]])
            i = i + 1
        s = self.paths[new][back[0]]

        # path includes first element of back
        self.state = front + s[:-1] + back
        
    def add_node(self):
        currpath = self.car_cycle.copy()
        # choose where to add
        if len(currpath) <= 2:
            addingLocation = 1
        else:
            addingLocation = np.random.randint(1, len(currpath) - 1)
        # "node to the left"
        target_neighbor = currpath[addingLocation - 1]
        #new_node = random.choice(self.neighbors[target_neighbor])
        new_node = random.choice(range(len(self.list_locations)))
        
        front = currpath[:addingLocation]
        back = currpath[addingLocation:]
        if(len(back) > 2):
            back = back[np.random.randint(1, len(back) - 1):]
        s1 = self.paths[front[-1]][new_node]
        s2 = self.paths[new_node][back[0]]
        self.state = front[:-1] + s1[:-1]+ s2[:-1] + back

    def energy(self):
        """
        Calculates the cost of the current DTH solution
        TODO: calculating the solution from scratch after a move prolly takes
              a lot of time; can improve this by having the move function
              return a delta which is prolly much faster to compute
        """
        self.gen_greedy_dropoff()  # generate dropoff mapping
        return cost_of_solution(self.g, self.car_cycle, self.dropoff_mapping)[0]

    def gen_best_state_dropoff(self):
        self.state = self.best_state
        self.gen_greedy_dropoff()

    def gen_greedy_dropoff(self):
        """
        Used for generating the droppoff mapping based on the current car cycle.

        Because the graph is connected, any node has a path to any other node
        so this will never not find a shortest path from a home to a location
        in the car cycle.
        """
        self.dropoff_mapping.clear()
        # iterate through all the TA homes and add them to the list corresponding
        # to the location such that the distance from that location to their home
        # is the shortest
        for home in [self.location_name_index_dict[home_name] for home_name in self.list_houses]:
            # find node in the cycle that is closest to the TA's home
            if home in self.car_cycle:  # if home in cycle drop TA off directly
                self.dropoff_mapping[home].append(home)
            else:
                # otherwise find the shortest path from the TA's home to any of the
                # nodes in the car's path
                paths_lengths_home = self.paths_lengths[home]
                closest_location = min(
                    np.unique(self.car_cycle),
                    key=lambda location: paths_lengths_home[location]
                )
                self.dropoff_mapping[closest_location].append(home)


    def get_shortest(self, node1: int, node: int):
        """
        Returns list corresponding to shortest path and the length of that path
        """
        return self.paths[node1][node2], self.paths_lengths[node1][node2]

    def location_name_to_index(self, location_name: str):
        return self.list_locations.index(location_name)
