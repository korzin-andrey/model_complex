import numpy as np

from ..Interface import BRModel


class AgeGroupBRModel(BRModel):
    AGE_GROUPS_NUMBER: 2

    def __init__(self):
        """
        Model for case of several age-group
        """
        self.alpha_len = 2
        self.beta_len = 4

    def simulate(
        self,
        alpha: list[float],
        beta: list[float],
        initial_infectious: list[int],
        population_size: int,
        modeling_duration: int
    ):
        """
        Simulate disease propagation.

        :param alpha: Fraction of non-immune people
        :param beta: Effective contacts intensivity
        :param initial_infectious: Numbers of initial infected people in the simulation
        :param rho: Numbers of people in simulation
        :param modeling_duration: duration of modeling

        :return:
        """
        assert len(alpha) == self.alpha_len
        assert len(beta) == self.beta_len
        assert len(initial_infectious) == self.AGE_GROUPS_NUMBER

        self.newly_infected = []

        for age_group_index in range(self.AGE_GROUPS_NUMBER):
            # SETTING UP INITIAL CONDITIONS
            total_infected = np.zeros(modeling_duration)
            newly_infected = np.zeros(modeling_duration)
            susceptible = np.zeros(modeling_duration)

            total_infected[0] = initial_infectious[age_group_index]
            newly_infected[0] = initial_infectious[age_group_index]

            initial_susceptible = int(alpha[age_group_index]*population_size)
            susceptible[0] = initial_susceptible

            # SIMULATION
            for day in range(modeling_duration-1):
                total_infected[day] = min(
                    sum(
                        newly_infected[day - tau] * self.br_function(tau)
                        for tau in range(len(self.br_func_array)) if (day - tau) >= 0
                    ),
                    population_size
                )

                newly_infected[day+1] = min(
                    sum(
                        beta[2*i + age_group_index] * susceptible[day] *
                        total_infected[day] / population_size
                        for i in range(self.AGE_GROUPS_NUMBER)
                    ),
                    susceptible[day]
                )

                susceptible[day+1] = susceptible[day] - newly_infected[day+1]

            self.newly_infected += list(newly_infected)

    def get_newly_infected(self):
        return self.newly_infected
