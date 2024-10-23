import scipy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymc as pm
from dateutil import parser

from ...epid_data import EpidData
from ..models import FactoryModel

class Calibration:

    def __init__(        
        self,
        incidence: str,
        initial_infectious: list[int],
        ) -> None:
        """
        Calibration class

        TODO

        :param incidence: Name of city  
        :param initial_infectious: Name of city  
        :param people_nums: Name of city  
        """

        self.model = FactoryModel.get_model(incidence)
        self.initial_infectious = initial_infectious

    def plot(self, city, path, start, end):
        epid_data = EpidData(city, path, parser.parse(start), parser.parse(end))
        BRModel = self.model
        data = BRModel.data_columns(epid_data)

        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        ax.plot(list(data), "o")


    def calibrate__abc(self, city, path, start, end): # -> 
        """
        TODO 
        :param city: Name of the city  
        :param path: Path to directory 'epid_data'
        :param start: First day of extracted data
            String of the form "mm-dd-yy"
        :param end: Last day of extracted data
            String of the form "mm-dd-yy"
        """

        epid_data = EpidData(city, path, parser.parse(start), parser.parse(end))

        BRModel = self.model
        data = BRModel.data_columns(epid_data)

        # TODO: выташить число людей

        def simulation_func(rng, alpha, beta, size=None):
            BRModel.simulate(alpha=alpha, beta=beta, initial_infectious=self.initial_infectious, rho=5e5, modeling_duration=len(data))
            return BRModel.get_newly_infected()
        
        with pm.Model() as model:
            alpha = pm.Uniform(name="alpha", lower=0, upper=1, )
            beta = pm.Uniform(name="beta", lower=0, upper=1, )
            sim = pm.Simulator("sim", simulation_func, params=(alpha, beta), 
                            epsilon=10, observed=data)
            idata = pm.sample_smc()
        self.model.is_calibrated = True
        return idata, simulation_func, data, self.model
    
    # TODO: write calibration method using optuna
    def calibrate_optuna():
        pass
