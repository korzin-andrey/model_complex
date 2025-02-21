import numpy as np

from ...utils import ModelParams
from ..Interface import Model


class AgeGroupBRModel(Model):
    GROUPS_NUMBER = 2

    def __init__(self):
        """
        Model for case of several age groups
        """
        self.alpha_dim = 2
        self.beta_dim = 4

    def simulate(self, params: ModelParams, modeling_duration: int):
        """
        Download epidemiological excel data file from the subdirectory of epid_data.
        epid_data directory looks like 'epid_data/{city}/epid_data.xlsx'.

        :param alpha: Fraction of non-immune people
        :param beta: Effective contacts intensivity
        :param initial_infectious: Numbers of initial infected people in the simulation
        :param rho: Numbers of people in simulation
        :param modeling_duration: duration of modeling

        :return:
        """
        alpha = params.alpha
        beta = params.beta
        initial_infectious = params.initial_infectious
        rho = params.population_size

        self.newly_infected = []
        self.prevalence = []
        self.recovered = []

        for j in range(self.GROUPS_NUMBER):
            # SETTING UP INITIAL CONDITIONS
            initial_susceptible = int(alpha[j] * rho)
            total_infected = np.zeros(modeling_duration)
            newly_infected = np.zeros(modeling_duration)
            susceptible = np.zeros(modeling_duration)
            recovered = np.zeros(modeling_duration)

            total_infected[0] = initial_infectious[j]
            newly_infected[0] = initial_infectious[j]
            susceptible[0] = initial_susceptible
            recovered[0] = 0

            # SIMULATION
            for day in range(modeling_duration - 1):
                total_infected[day] = min(
                    sum(
                        newly_infected[day - tau] * self.br_function(tau)
                        for tau in range(len(self.br_func_array))
                        if (day - tau) >= 0
                    ),
                    rho,
                )

                recovered[day] = (
                    initial_susceptible - susceptible[day] - total_infected[day]
                )

                newly_infected[day + 1] = min(
                    sum(
                        beta[2 * i + j] * susceptible[day] * total_infected[day] / rho
                        for i in range(self.GROUPS_NUMBER)
                    ),
                    susceptible[day],
                )

                susceptible[day + 1] = susceptible[day] - newly_infected[day + 1]

            self.newly_infected += list(newly_infected)
            self.prevalence += list(total_infected)
            self.recovered += list(recovered)
