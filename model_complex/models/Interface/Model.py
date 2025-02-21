import numpy as np

from ...utils import ModelParams


class Model:
    GROUPS_NUMBER = 0

    br_func_array = [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05]

    is_ci_ready = False
    is_calibrated = False
    calibration_params: ModelParams = None
    ci_params: list[ModelParams] = None
    newly_infected: list = None
    prevalence: list = None
    recovered: list = None

    def __init__(self):
        """
        Interface for all Models
        """
        self.alpha_dim = 0
        self.beta_dim = 0

    def simulate(self, params: ModelParams, modeling_duration: int):
        pass

    def br_function(self, day: int) -> int:
        """
        Baroyan-Rvachev function

        :param day: Illness day

        :return: human virulence
        """

        if day >= len(self.br_func_array):
            return 0
        return self.br_func_array[day]

    def params(self):
        """
        TODO
        """
        return (self.alpha_dim, self.beta_dim)

    def get_daily_newly_infected(self):
        return self.newly_infected

    def get_daily_newly_infected_by_group(self):
        return np.array_split(self.newly_infected, self.GROUPS_NUMBER)

    def get_weekly_newly_infected(self):
        return np.array(self.newly_infected).reshape(-1, 7).sum(axis=1)

    def get_weekly_newly_infected_by_group(self):
        return self.get_weekly_newly_infected().reshape(self.alpha_dim, -1)

    def get_daily_prevalence(self):
        return self.prevalence

    def get_daily_prevalence_by_group(self):
        return np.array_split(self.prevalence, self.GROUPS_NUMBER)

    def get_weekly_prevalence(self):
        return np.array(self.prevalence).reshape(-1, 7).sum(axis=1)

    def get_weekly_prevalence_by_group(self):
        return self.get_weekly_prevalence().reshape(self.alpha_dim, -1)

    def get_daily_recovered(self):
        return self.recovered

    def get_daily_recovered_by_group(self):
        return np.array_split(self.recovered, self.GROUPS_NUMBER)

    def get_weekly_recovered(self):
        return np.array(self.recovered).reshape(-1, 7).sum(axis=1)

    def get_weekly_recovered_by_group(self):
        return self.get_weekly_recovered().reshape(self.alpha_dim, -1)

    def set_best_params(self, best_params: ModelParams):
        self.calibration_params = best_params
        self.is_calibrated = True

    def set_ci_params(self, ci_params: list[ModelParams]):
        self.ci_params = ci_params
        self.is_ci_ready = True

    def get_best_params(self) -> ModelParams:
        if self.is_calibrated:
            return self.calibration_params
        else:
            raise Exception("Model is not calibrated!")

    def get_ci_params(self) -> list[ModelParams]:
        if self.is_ci_ready:
            return self.ci_params
        else:
            raise Exception("Model does not have set of parameters for CI construction!")
