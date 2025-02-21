import numpy as np

from ...utils import ModelParams
from ..Interface import Model


class TotalBRModel(Model):
    GROUPS_NUMBER = 1

    def __init__(self):
        """
        Model for total case
        """
        self.alpha_dim = 1
        self.beta_dim = 1

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

        # SETTING UP INITIAL CONDITIONS
        initial_susceptible = int(alpha[0] * rho)
        total_infected = np.zeros(modeling_duration)
        newly_infected = np.zeros(modeling_duration)
        susceptible = np.zeros(modeling_duration)
        recovered = np.zeros(modeling_duration)

        total_infected[0] = initial_infectious[0]
        newly_infected[0] = initial_infectious[0]
        susceptible[0] = initial_susceptible
        recovered[0] = 0

        # SIMULATION
        for day in range(modeling_duration - 1):
            total_infected[day] = min(
                sum(
                    [
                        newly_infected[day - tau] * self.br_function(tau)
                        for tau in range(len(self.br_func_array))
                        if (day - tau) >= 0
                    ]
                ),
                rho,
            )

            recovered[day] = initial_susceptible - susceptible[day] - total_infected[day]

            newly_infected[day + 1] = min(
                beta[0] * susceptible[day] * total_infected[day] / rho, susceptible[day]
            )
            susceptible[day + 1] = susceptible[day] - newly_infected[day + 1]
        self.susceptible = susceptible
        self.newly_infected = newly_infected
        self.prevalence = total_infected
        self.recovered = recovered
