import numpy as np
import optuna
import pandas as pd
import pymc as pm
from scipy.optimize import dual_annealing
from sklearn.metrics import r2_score

from ..models import BRModel

optuna.logging.set_verbosity(optuna.logging.ERROR)


class Calibration:

    def __init__(
        self,
        init_infectious: list[int],
        model: BRModel,
        data: list,
        rho: int,
    ) -> None:
        """
        Calibration class

        TODO

        :param init_infectious: Number of initial infected people
        :param model: Model for calibration
        :param data: Observed data for calibrating process
        :param rho: People's population
        """
        self.rho = rho
        self.init_infectious = init_infectious
        self.model = model
        self.data = data

    def abc_calibration(self, sample=100, epsilon=3000):
        """
        TODO

        """

        alpha_len, beta_len = self.model.params()

        def simulation_func(rng, alpha, beta, size=None):
            self.model.simulate(
                alpha=alpha,
                beta=beta,
                initial_infectious=self.init_infectious,
                rho=self.rho,
                modeling_duration=int(len(self.data) / alpha_len),
            )
            return self.model.newly_infected

        with pm.Model() as model:
            alpha = pm.Uniform(name="alpha", lower=0, upper=1, shape=(alpha_len,))
            beta = pm.Uniform(name="beta", lower=0, upper=1, shape=(beta_len,))

            sim = pm.Simulator(
                "sim",
                simulation_func,
                list(alpha) + [0] * (beta_len - alpha_len),
                beta,
                epsilon=epsilon,
                observed=self.data,
            )

            idata = pm.sample_smc(progressbar=False)

        posterior = idata.posterior.stack(samples=("draw", "chain"))

        alpha = [
            np.random.choice(posterior["alpha"][i], size=sample)
            for i in range(alpha_len)
        ]
        beta = [
            np.random.choice(posterior["beta"][i], size=sample) for i in range(beta_len)
        ]

        return alpha, beta

    def optuna_calibration(self, n_trials=1000):
        """
        TODO

        """

        alpha_len, beta_len = self.model.params()

        def model(trial):

            alpha = [trial.suggest_float(f"alpha_{i}", 0, 1) for i in range(alpha_len)]
            beta = [trial.suggest_float(f"beta_{i}", 0, 1) for i in range(beta_len)]

            self.model.simulate(
                alpha=alpha,
                beta=beta,
                initial_infectious=self.init_infectious,
                rho=self.rho,
                modeling_duration=int(len(self.data) / alpha_len),
            )

            return r2_score(self.data, self.model.newly_infected)

        study = optuna.create_study(direction="maximize")
        study.optimize(model, n_trials=n_trials)

        alpha = [study.best_params[f"alpha_{i}"] for i in range(alpha_len)]
        beta = [study.best_params[f"beta_{i}"] for i in range(beta_len)]

        # запускаем, чтобы в модели были результаты с лучшими параметрами
        self.model.simulate(
            alpha=alpha,
            beta=beta,
            initial_infectious=self.init_infectious,
            rho=self.rho,
            modeling_duration=int(len(self.data) / alpha_len),
        )

        return alpha, beta

    def annealing_calibration(self):
        """
        TODO

        """

        alpha_len, beta_len = self.model.params()

        lw = [0] * (alpha_len + beta_len)
        up = [1] * (alpha_len + beta_len)

        def model(x):

            alpha = x[:alpha_len]
            beta = x[alpha_len:]

            self.model.simulate(
                alpha=alpha,
                beta=beta,
                initial_infectious=self.init_infectious,
                rho=self.rho,
                modeling_duration=int(len(self.data) / alpha_len),
            )

            return -r2_score(self.data, self.model.newly_infected)

        ret = dual_annealing(model, bounds=list(zip(lw, up)))

        alpha = ret.x[:alpha_len]
        beta = ret.x[alpha_len:]

        # запускаем, чтобю в модели были результаты с лучшими параметрами
        self.model.simulate(
            alpha=alpha,
            beta=beta,
            initial_infectious=self.init_infectious,
            rho=self.rho,
            modeling_duration=int(len(self.data) / alpha_len),
        )

        return alpha, beta
