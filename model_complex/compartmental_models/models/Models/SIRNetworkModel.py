import numpy as np
import networkx as nx
import EoN
import random
from collections import defaultdict
from .ModelParams import ModelParams


def fast_SIR_immune(G, alpha, beta, initial_infecteds_number=None, initial_recovereds=None,
                    rho=None, tmin=0, tmax=float('Inf'), transmission_weight=None,
                    recovery_weight=None, return_full_data=False, sim_kwargs=None):
    gamma = 1
    nodes = list(G.nodes)
    assert (alpha > 0) and (alpha < 1), "Incorrect alpha value!"
    initial_infecteds = random.sample(
        nodes, min(initial_infecteds_number, len(nodes)))
    initial_immune_number = int(G.order()*(1-alpha))
    initial_recovereds = random.sample(
        list(set(nodes) - set(initial_infecteds)),
        min(initial_immune_number, len(nodes) - len(initial_infecteds)))
    return EoN.fast_SIR(G, tau=beta, gamma=gamma, initial_infecteds=initial_infecteds,
                        initial_recovereds=initial_recovereds, tmax=100)


class SIRNetworkModel():
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
        self.alpha_dim = 1
        self.beta_dim = 1
        self.is_calibrated = False
        self.ready_for_ci = False
        self.best_calibration_params: ModelParams = None
        self.ci_params: list[ModelParams] = None

    def simulate(
        self,
        model_params: ModelParams,
        modeling_duration: int
    ):
        """
        Simulate disease propagation using SIR on network.

        :return:
        """
        # time, susceptible, total_infected, recovered = \
        #     fast_SIR_immune(self.G, beta=model_params.beta[0],
        #                     initial_infecteds_number=model_params.initial_infectious[0],
        #                     alpha=model_params.alpha[0], tmax=modeling_duration)
        time, susceptible, total_infected, recovered = \
            EoN.fast_SIR(self.G, tau=model_params.beta[0],
                         gamma=1, rho=0.005, tmax=modeling_duration)
        # TODO: check equation for calculating newly_infected from
        # total_infected and recovered
        susceptible = susceptible[:modeling_duration]
        total_infected = total_infected[:modeling_duration]
        recovered = recovered[:modeling_duration]
        time = time[:modeling_duration]
        self.newly_infected = [total_infected[0] if index == 0 else
                               total_infected[index] -
                               (total_infected[index-1] -
                                abs(recovered[index] - recovered[index-1]))
                               for index in range(len(total_infected))]
        assert len(self.newly_infected) == modeling_duration

    def get_daily_newly_infected(self):
        return self.newly_infected

    def pad_array_to_multiple_of_seven(self, arr):
        '''
        Auxiliary function used for padding array of daily data by zeroes for converting
        to weekly data
        '''
        current_size = len(arr)
        new_size = (current_size + 6) // 7 * 7
        padding_needed = new_size - current_size
        padded_array = np.pad(arr, (0, padding_needed),
                              mode='constant', constant_values=0)
        return padded_array

    def get_weekly_newly_infected(self):
        daily_newly_infected_padded = self.pad_array_to_multiple_of_seven(
            self.newly_infected)
        return daily_newly_infected_padded.reshape(-1, 7).sum(axis=1)

    def set_best_params_after_calibration(self, best_params: ModelParams):
        self.best_calibration_params = best_params
        self.is_calibrated = True

    def set_ci_params(self, ci_params: ModelParams):
        self.ci_params = ci_params
        self.ready_for_ci = True

    def get_best_params(self) -> ModelParams:
        if self.is_calibrated:
            return self.best_calibration_params
        else:
            raise Exception('Model is not calibrated!')

    def get_ci_params(self) -> list[ModelParams]:
        if self.ready_for_ci:
            return self.ci_params
        else:
            raise Exception(
                'Model does not have set of parameters for CI construction!')
