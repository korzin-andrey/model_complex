import pymc as pm
import pandas as pd
import optuna
from sklearn.metrics import r2_score

from ..models import BRModel

class Calibration:

    def __init__(        
        self,
        init_infectious: list[int]|int,
        model: BRModel,
        data: list,
        rho: int
        ) -> None:
        """
        Calibration class

        TODO

        :param init_infectious: Number of initial infected people  
        :param model: Model for calibration  
        :param data: Observed data for calibrating process 
        :param rho: Population size 
        """
        self.init_infectious = init_infectious
        self.model = model
        self.data = data
        self.rho = rho


    def abc_calibration(self):
        """
        TODO

        """
        def simulation_func(rng, alpha, beta, size=None):
            self.model.simulate(
                alpha=alpha,
                beta=beta,
                initial_infectious=self.init_infectious,
                rho=self.rho,
                modeling_duration=int(len(self.data)/self.model.alpha_len)
            )
            return self.model.get_newly_infected()
        
        with pm.Model() as model:
            alpha = pm.Uniform(name="a", lower=0,
                               upper=1, shape=(self.model.alpha_len, ))
            beta = pm.Uniform(name="b", lower=0, 
                              upper=1, shape=(self.model.beta_len, ))

            sim = pm.Simulator("sim", simulation_func, alpha, beta,
                            epsilon=10, observed=self.data)
            
            idata = pm.sample_smc(progressbar=False)

        return idata, self.data, simulation_func
    
    def optuna_calibration(self):
        
        def model(trial):
            alpha = trial.suggest_float('alpha', 0, 1)
            beta = trial.suggest_float('beta', 0, 1)
            return r2_score

        #study =  optuna.create_study(study_name=study_name, storage=storage_name, sampler=optuna.samplers.TPESampler(), 
        #                             pruner=optuna.pruners.HyperbandPruner, load_if_exists=True, 
        #                             direction="maximize")
        study = optuna.create_study(sampler=optuna.samplers.CmaEsSampler(), direction="maximize")
        n_trials = 5000
        study.optimize(model, n_trials=n_trials)