import numpy as np
import pymc as pm
import scipy
import typing as tp

from ..Interface import BRModel
from .ModelParams import ModelParams


class TotalBRModel(BRModel):
    def __init__(self):
        """
        Model for total case
        """
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
        Launch simulation using Baroyan-Rvachev model

        :param alpha: Fraction of non-immune people
        :param beta: Effective contacts intensivity
        :param initial_infectious: Numbers of initial infected people in the simulation
        :param population_size: Numbers of people in simulation
        :param modeling_duration: duration of modeling

        :return:
        """
        assert len(model_params.alpha) == self.alpha_dim
        assert len(model_params.beta) == self.beta_dim
        assert len(model_params.initial_infectious) == self.alpha_dim
        assert np.all(np.array(model_params.alpha) > 0) and np.all(
            np.array(model_params.alpha) < 1)

        # SETTING UP INITIAL CONDITIONS
        initial_susceptible = int(
            model_params.alpha[0]*model_params.population_size)
        initial_infectious = model_params.initial_infectious
        total_infected = np.zeros(modeling_duration)
        newly_infected = np.zeros(modeling_duration)
        susceptible = np.zeros(modeling_duration)
        total_infected[0] = initial_infectious[0]
        newly_infected[0] = initial_infectious[0]
        susceptible[0] = initial_susceptible

        # SIMULATION
        for day in range(modeling_duration-1):
            total_infected[day] = min(sum([newly_infected[day - tau]*self.br_function(tau)
                                           for tau in range(len(self.br_func_array)) if (day - tau) >= 0]),
                                      model_params.population_size)

            newly_infected[day+1] = min(model_params.beta[0]*susceptible[day]*total_infected[day]/model_params.population_size,
                                        susceptible[day])
            susceptible[day+1] = susceptible[day] - newly_infected[day+1]

        self.newly_infected = newly_infected

    def get_newly_infected(self):
        return self.newly_infected

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
