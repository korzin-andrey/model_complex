import pymc as pm
import pandas as pd
import optuna
from sklearn.metrics import r2_score
import numpy as np

from ..models import BRModel

optuna.logging.set_verbosity(optuna.logging.ERROR)

class Calibration:

    def __init__(        
        self,
        init_infectious: list[int]|int,
        model: BRModel,
        data: pd.DataFrame,
        ) -> None:
        """
        Calibration class

        TODO

        :param init_infectious: Number of initial infected people  
        :param model: Model for calibration  
        :param data: Observed data for calibrating process  
        """

        self.init_infectious = init_infectious
        self.model = model
        self.data = data


    def abc_calibration(self):
        """
        TODO

        """

        rho = self.data['population_age_0-14'].iloc[-1] + self.data['population_age_15+'].iloc[-1]

        data, alpha_len, beta_len = self.model.params(self.data)

        def simulation_func(rng, alpha, beta, size=None):
            self.model.simulate(
                alpha=alpha, 
                beta=beta, 
                initial_infectious=self.init_infectious, 
                rho=round(rho/10), 
                modeling_duration=int(len(data)/alpha_len)
            )
            return self.model.newly_infected
        
        with pm.Model() as model:
            alpha = pm.Uniform(name="alpha", lower=0, upper=1, shape=(alpha_len,))
            beta = pm.Uniform(name="beta", lower=0, upper=1, shape=(beta_len,))


            sim = pm.Simulator("sim", simulation_func, alpha, beta,
                            epsilon=5, observed=data)
            
            idata = pm.sample_smc()

        posterior = idata.posterior.stack(samples=("draw", "chain"))


        alpha = [np.random.choice(posterior["alpha"][i], size=100) for i in range(alpha_len)]
        beta = [np.random.choice(posterior["beta"][i], size=100) for i in range(beta_len)]
        
        return posterior, round(rho/10)
    

    def optuna_calibration(self):

        rho = self.data['population_age_0-14'].iloc[-1] + self.data['population_age_15+'].iloc[-1]

        data, alpha_len, beta_len = self.model.params(self.data)

        def model(trial):

            alpha = []
            beta = []
            
            for i in range(alpha_len):
                alpha.append( trial.suggest_float(f'alpha_{i}', 0, 1) )

            for i in range(beta_len):
                beta.append( trial.suggest_float(f'beta_{i}', 0, 1) )

            self.model.simulate(
                alpha=alpha, 
                beta=beta, 
                initial_infectious=self.init_infectious, 
                rho=round(rho/10), 
                modeling_duration=int(len(data)/alpha_len)
            )

            return r2_score(data, self.model.newly_infected)


        study = optuna.create_study(direction="maximize")
        n_trials = 5000
        study.optimize(model, n_trials=n_trials)

        alpha = [study.best_params[f'alpha_{i}'] for i in range(alpha_len)]
        beta = [study.best_params[f'beta_{i}'] for i in range(beta_len)]

        return alpha, beta, round(rho/10)