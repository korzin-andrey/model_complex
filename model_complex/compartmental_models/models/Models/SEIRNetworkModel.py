import numpy as np
import networkx as nx
import EoN
import random
from collections import defaultdict

from .ModelParams import ModelParams


class SEIRNetworkModel():
    def __init__(self, population_size: int, m_vertices: int):
        """
        SIR network model with immune fraction added.
        :param: population_size: number of vertices in network
        :param m_vertices: number of vertices to link with new one according
        to preferential attachment (see A. L. Barabási and R. Albert “Emergence of 
        scaling in random networks”, Science 286, pp 509-512, 1999.)
        """
        assert isinstance(
            population_size, int), "Population type should be int."
        assert population_size > 10**2, "Too small population size!"
        self.population_size = population_size
        self.m_vertices = m_vertices
        # TODO: decide which type of network to use
        self.G = nx.barabasi_albert_graph(population_size, m_vertices)
        self.alpha_len = 1
        self.beta_len = 1

    def simulate(
        self,
        model_params: ModelParams,
        modeling_duration: int
    ):
        """
        Simulate disease propagation using SIR on network.

        :return:
        """
        node_attribute_dict = {node: 0.5+random.random()
                               for node in self.G.nodes()}
        edge_attribute_dict = {edge: 0.5+random.random()
                               for edge in self.G.edges()}

        nx.set_node_attributes(
            self.G, values=node_attribute_dict, name='expose2infect_weight')
        nx.set_edge_attributes(
            self.G, values=edge_attribute_dict, name='transmission_weight')

        H = nx.DiGraph()
        H.add_node('S')
        H.add_edge('E', 'I', rate=0.6, weight_label='expose2infect_weight')
        H.add_edge('I', 'R', rate=0.1)
        J = nx.DiGraph()
        J.add_edge(('I', 'S'), ('I', 'E'), rate=0.1,
                   weight_label='transmission_weight')

        IC = defaultdict(lambda: 'S')
        for node in range(200):
            IC[node] = 'I'

        return_statuses = ('S', 'E', 'I', 'R')

        time, susceptible, exposed, total_infected, recovered = \
            EoN.Gillespie_simple_contagion(self.G, H, J, IC, return_statuses,
                                           tmax=float('Inf'))

        newly_infected = [total_infected[0] if index == 0 else
                          total_infected[index] - (total_infected[index-1] -
                          abs(recovered[index] - recovered[index-1]))
                          for index in range(len(total_infected))]
        self.newly_infected = newly_infected

    def get_newly_infected(self):
        return self.newly_infected
