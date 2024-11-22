import numpy as np
import pymc as pm

from ..Interface import BRModel


class AgeGroupBRModel(BRModel):

    def __init__(self):
        """
        Model for case of several age groups
        """
        self.alpha_len = 2
        self.beta_len = 4

    def simulate(
        self,
        alpha: list[float],
        beta: list[float],
        initial_infectious: list[int],
        rho: int,
        modeling_duration: int,
    ):
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
        # assert (
        #     len(alpha) == self.beta_len
        # ), f"Размерность alpha={self.alpha_len}, а получена {len(alpha)}"
        # assert (
        #     len(beta) == self.beta_len
        # ), f"Размерность beta={self.beta_len}, а получена {len(beta)}"
        # assert (
        #     len(initial_infectious) == self.alpha_len
        # ), f"Размерность initial_infectious={self.alpha_len}, а получена {len(initial_infectious)}"

        self.newly_infected = []

        for j in range(2):
            # SETTING UP INITIAL CONDITIONS
            total_infected = np.zeros(modeling_duration)
            newly_infected = np.zeros(modeling_duration)
            susceptible = np.zeros(modeling_duration)

            total_infected[0] = initial_infectious[j]
            newly_infected[0] = initial_infectious[j]

            initial_susceptible = int(alpha[j] * rho)
            susceptible[0] = initial_susceptible

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

                newly_infected[day + 1] = min(
                    sum(
                        beta[2 * i + j] * susceptible[day] * total_infected[day] / rho
                        for i in range(2)
                    ),
                    susceptible[day],
                )

                susceptible[day + 1] = susceptible[day] - newly_infected[day + 1]

            self.newly_infected += list(newly_infected)
