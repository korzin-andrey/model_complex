import pymc as pm
import pandas as pd
import numpy as np
import optuna
from sklearn.metrics import r2_score
import scipy

from ..models import BRModel, SIRNetworkModel
from ..models.Models.ModelParams import ModelParams

pd.options.mode.copy_on_write = True


class Calibration:

    def __init__(
        self,
        model: BRModel | SIRNetworkModel,
        data: list,
        model_params: ModelParams,
    ) -> None:
        """
        Calibration class
        TODO 
        :param init_infectious: Number of initial infected people  
        :param model: Model for calibration  
        :param data: Observed data for calibrating process 
        :param rho: Population size 
        """
        self.model = model
        self.data = data
        self.model_params = model_params
        # self.init_infectious = init_infectious
        # self.population_size = population_size

    def abc_calibration(self):
        """
        TODO

        """
        def simulation_func(rng, alpha, beta, size=None):
            model_params = ModelParams(population_size=self.model_params.population_size,
                                       initial_infectious=self.model_params.initial_infectious,
                                       alpha=alpha, beta=beta)
            self.model.simulate(
                model_params,
                modeling_duration=int(len(self.data)/self.model.alpha_dim)
            )
            return self.model.newly_infected

        with pm.Model() as model:
            alpha = pm.Uniform(name="alpha", lower=0,
                               upper=1, shape=(self.model.alpha_dim, ))
            beta = pm.Uniform(name="beta", lower=0,
                              upper=1, shape=(self.model.beta_dim, ))
            # TODO: change strange approach for setting up equal dimensions for params
            sim = pm.Simulator("sim", simulation_func,
                               [*list(alpha)] + [0] *
                               (self.model.beta_dim-self.model.alpha_dim),
                               beta, epsilon=3500, observed=self.data)
            idata = pm.sample_smc(progressbar=False)
        posterior = idata.posterior.stack(samples=("draw", "chain"))
        alpha = [np.random.choice(posterior["alpha"][i],
                                  size=100) for i in range(self.model.alpha_dim)]
        beta = [np.random.choice(posterior["beta"][i],
                                 size=100) for i in range(self.model.beta_dim)]
        return alpha, beta

    def optuna_calibration(self, n_trials=1000):
        alpha_len, beta_len = self.model.params()

        def model(trial):

            alpha = [trial.suggest_float(
                f"alpha_{i}", 0, 1) for i in range(alpha_len)]
            beta = [trial.suggest_float(f"beta_{i}", 0, 1)
                    for i in range(beta_len)]

            self.model.simulate(
                alpha=alpha,
                beta=beta,
                initial_infectious=self.init_infectious,
                population_size=self.population_size,
                modeling_duration=int(len(self.data) / alpha_len),
            )

            return r2_score(self.data, self.model.newly_infected)

        study = optuna.create_study(direction="maximize")
        study.optimize(model, n_trials=n_trials)

        alpha = [study.best_params[f"alpha_{i}"] for i in range(alpha_len)]
        beta = [study.best_params[f"beta_{i}"] for i in range(beta_len)]
        self.model.simulate(
            alpha=alpha,
            beta=beta,
            initial_infectious=self.init_infectious,
            population_size=self.population_size,
            modeling_duration=int(len(self.data) / alpha_len),
        )
        return alpha, beta

    def annealing_calibration(self):
        """
        TODO
        """
        alpha_dim, beta_dim = self.model.alpha_dim, self.model.beta_dim
        # lw = [0.01] * (alpha_dim + beta_dim) + [int(0.001*self.model_params.population_size)] * \
        #     len(self.model_params.initial_infectious)
        # up = [0.98] * (alpha_dim + beta_dim) + [int(0.1*self.model_params.population_size)] * \
        #     len(self.model_params.initial_infectious)
        lw = [0.7, 0.01, 1]
        up = [0.999, 0.16, 10]

        def model(x):
            alpha = x[:alpha_dim]
            beta = x[alpha_dim:alpha_dim+beta_dim]
            initial_infectious = x[alpha_dim+beta_dim:]
            params = ModelParams(population_size=self.model_params.population_size,
                                 initial_infectious=initial_infectious,
                                 alpha=alpha, beta=beta)
            self.model.simulate(params,
                                modeling_duration=int(len(self.data) / alpha_dim))
            return -r2_score(self.data, self.model.newly_infected)

        ret = scipy.optimize.dual_annealing(
            model, bounds=list(zip(lw, up)), maxiter=1000)

        self.model_params.alpha = ret.x[:alpha_dim]
        self.model_params.beta = ret.x[alpha_dim:alpha_dim+beta_dim]
        self.model_params.initial_infectious = [
            int(elem) for elem in ret.x[alpha_dim+beta_dim:]]

        # simulate with best params
        self.model.simulate(self.model_params,
                            modeling_duration=int(len(self.data) / alpha_dim))
        return self.model_params.alpha, self.model_params.beta

    def mcmc_calibration(
        self,
        sample=100,
        epsilon=10000,
        with_rho=False,  # [50_000, 500_000] - если True
        with_initi=False,  # [1, 1_000] - если True
        tune=2500,
        draws=500,
        chains=4,
    ):
        """
        Parameters:
            - with_rho -- tune population size
            - with_initi -- tune initial infected
            - tune -- number of mcmc warmup samples
            - draws -- number of mcmc draws
            - chains -- number of chains
        """

        alpha_len, beta_len = self.model.params()
        init_infectious = self.init_infectious
        population_size = self.population_size

        def simulation_func(rng, alpha, beta, population_size, init_infectious, size=None):

            self.model.simulate(
                alpha=alpha,
                beta=beta,
                initial_infectious=init_infectious,
                population_size=population_size,
                modeling_duration=len(self.data) // alpha_len,
            )
            return self.model.newly_infected

        with pm.Model() as pm_model:
            alpha = pm.Uniform(name="alpha", lower=0,
                               upper=1, shape=(alpha_len,))
            beta = pm.Uniform(name="beta", lower=0, upper=1, shape=(beta_len,))

            if with_rho:
                population_size = pm.Uniform(
                    name="rho", lower=with_rho[0], upper=with_rho[1])

            if with_initi:
                init_infectious = pm.Uniform(
                    name="init_infectious",
                    lower=with_initi[0],
                    upper=with_initi[1],
                    shape=(alpha_len,),
                )

            sim = pm.Simulator(
                "sim",
                simulation_func,
                alpha,
                beta,
                population_size,
                init_infectious,
                epsilon=epsilon,
                ndims_params=[alpha_len, beta_len, 1, alpha_len],
                observed=self.data,
            )

            # Differential evolution (DE) Metropolis sampler
            # step=pm.DEMetropolisZ(proposal_dist=pm.LaplaceProposal)
            step = pm.DEMetropolisZ()

            idata = pm.sample(
                tune=tune,
                draws=draws,
                chains=chains,
                step=step,
                progressbar=False,
            )
            idata.extend(pm.sample_posterior_predictive(
                idata, progressbar=False))

        posterior = idata.posterior.stack(samples=("draw", "chain"))

        alpha = [
            np.random.choice(posterior["alpha"][i], size=sample)
            for i in range(alpha_len)
        ]
        beta = [
            np.random.choice(posterior["beta"][i], size=sample) for i in range(beta_len)
        ]

        return alpha, beta
