import optuna

from ..models import Model
from ..utils import ModelParams
from .Algorithms import ABC, MCMC, Annealing, Optuna

optuna.logging.set_verbosity(optuna.logging.ERROR)


class Calibration:

    def __init__(
        self,
        model: Model,
        data: list,
        model_params: ModelParams,
    ) -> None:
        """
        Calibration class

        TODO

        :param init_infectious: Number of initial infected people
        :param model: Model for calibration
        :param data: Observed data for calibrating process
        :param rho: People's population
        """
        self.model = model
        self.model_params = model_params
        self.time_step = data.attrs["time_step"]
        self.data = data.drop(columns=["datetime"]).to_numpy().T.flatten()

    def abc_calibration(self, sample=100, epsilon=3000):

        ABC.calibrate(
            model=self.model,
            data=self.data,
            time_step=self.time_step,
            model_params=self.model_params,
            sample=sample,
            epsilon=epsilon,
        )

    def optuna_calibration(self, n_trials=1000):

        Optuna.calibrate(
            model=self.model,
            data=self.data,
            time_step=self.time_step,
            model_params=self.model_params,
            n_trials=n_trials,
        )

    def annealing_calibration(self):

        Annealing.calibrate(
            model=self.model,
            data=self.data,
            time_step=self.time_step,
            model_params=self.model_params,
        )

    def mcmc_calibration(
        self,
        sample=100,
        epsilon=10000,
    ):

        MCMC.calibrate(
            model=self.model,
            data=self.data,
            time_step=self.time_step,
            model_params=self.model_params,
            sample=sample,
            epsilon=epsilon,
        )
