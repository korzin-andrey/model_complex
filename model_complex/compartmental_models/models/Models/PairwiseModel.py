import numpy as np
import networkx as nx
import EoN


class PairwiseModel():
    def __init__(self, population_size, m_vertices):
        """
        Pairwise model
        """
        assert isinstance(
            population_size, int), "Population type should be int."
        assert population_size > 10**2, "Too small population size!"
        self.population_size = population_size
        self.m_vertices = m_vertices
        self.G = nx.barabasi_albert_graph(population_size, m_vertices)

    def simulate(
        self,
        tau: float,
        gamma: float,
        init_inf_frac: float,
        modeling_duration: int,
    ):
        """
        Simulate disease propagation using edge based compartmental
        model (aka pairwise) on Barabashi-Albert network.

        :param tau: Transmission rate
        :param gamma:  
        :param init_inf_frac: Fraction of initially infected
        :param rho: Numbers of people in simulation
        :param modeling_duration: duration of modeling
        :param m_vertices: number of vertices to link with new one according
        to preferential attachment (see A. L. Barabási and R. Albert “Emergence of 
        scaling in random networks”, Science 286, pp 509-512, 1999.)
        :return:
        """
        assert 0 < init_inf_frac < 1, "Initial infectious fraction should be from 0 to 1."
        # !!! rho here is NOT population size
        time, susceptible, total_infected, recovered = \
            EoN.EBCM_from_graph(self.G, tau, gamma, rho=init_inf_frac,
                                tmax=modeling_duration)
        # TODO: check equation for calculating newly_infected from
        # total_infected and recovered
        newly_infected = [total_infected[0] if index == 0 else
                          total_infected[index] - (total_infected[index-1] -
                          abs(recovered[index] - recovered[index-1]))
                          for index in range(modeling_duration)]
        assert len(newly_infected) == modeling_duration
        self.newly_infected = newly_infected

    def get_newly_infected(self):
        return self.newly_infected
