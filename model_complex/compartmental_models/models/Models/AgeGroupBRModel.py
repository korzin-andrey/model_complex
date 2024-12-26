import numpy as np

from ..Interface import BRModel
from .ModelParams import ModelParams


class AgeGroupBRModel(BRModel):
    AGE_GROUPS_NUMBER = 2

    def __init__(self):
        """
        Model for case of several age-group
        """
        self.alpha_dim = 2
        self.beta_dim = 4

    def simulate(
        self,
        model_params: ModelParams,
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
        assert len(model_params.alpha) == self.alpha_dim
        assert len(model_params.beta) == self.beta_dim
        assert len(model_params.initial_infectious) == self.alpha_dim
        assert np.all(np.array(model_params.alpha) > 0) and np.all(
            np.array(model_params.alpha) < 1)

        self.newly_infected = []

        for age_group_index in range(self.AGE_GROUPS_NUMBER):
            # SETTING UP INITIAL CONDITIONS
            total_infected = np.zeros(modeling_duration)
            newly_infected = np.zeros(modeling_duration)
            susceptible = np.zeros(modeling_duration)

            total_infected[0] = model_params.initial_infectious[age_group_index]
            newly_infected[0] = model_params.initial_infectious[age_group_index]

            initial_susceptible = int(
                model_params.alpha[age_group_index]*model_params.population_size)
            susceptible[0] = initial_susceptible

            # SIMULATION
            for day in range(modeling_duration-1):
                total_infected[day] = min(
                    sum(
                        newly_infected[day - tau] * self.br_function(tau)
                        for tau in range(len(self.br_func_array)) if (day - tau) >= 0
                    ),
                    model_params.population_size
                )

                newly_infected[day+1] = min(
                    sum(
                        model_params.beta[2*i + age_group_index] * susceptible[day] *
                        total_infected[day] / model_params.population_size
                        for i in range(AgeGroupBRModel.AGE_GROUPS_NUMBER)
                    ),
                    susceptible[day]
                )
                susceptible[day+1] = susceptible[day] - newly_infected[day+1]
            self.newly_infected += list(newly_infected)

    def get_daily_newly_infected(self):
        age_data_arrays = np.array_split(
            self.newly_infected, AgeGroupBRModel.AGE_GROUPS_NUMBER)
        return {index: age_data_arrays[index] for index in range(AgeGroupBRModel.AGE_GROUPS_NUMBER)}
