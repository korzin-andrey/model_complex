import scipy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymc as pm
from dateutil import parser

from .epid_data import EpidData
from ..models import FactoryBRModel

class Calibration:

    def __init__(        
        self,
        incidence: int,
        initial_infectious: list[int],
        ) -> None:
        """
        Calibration class

        TODO

        :param incidence: Name of city  
        :param initial_infectious: Name of city  
        :param people_nums: Name of city  
        """

        self.Model = FactoryBRModel.get_model(incidence)
        self.initial_infectious = initial_infectious


    def calibrate(self, city, path, start, end): # -> 
        """
        TODO

        :param city: Name of city  
        :param path: path to directory 'epid_data'
        :param start: First day of extracted data
            String of the form "mm-dd-yy"
        :param end: Last day of extracted data
            String of the form "mm-dd-yy"
        """

        epid_data = EpidData(city, path, parser.parse(start), parser.parse(end))


        data, alpha_len, beta_len = self.Model.params(epid_data)

        def simulation_func(rng, alpha, beta, size=None):
            self.Model.simulate(
                alpha=alpha, 
                beta=beta, 
                initial_infectious=self.initial_infectious, 
                rho=5e5, 
                modeling_duration=int(len(data)/alpha_len[0])
            )
            return self.Model.get_newly_infected()
        
        with pm.Model() as model:
            alpha = pm.Uniform(name="a", lower=0, upper=1, shape=alpha_len)
            beta = pm.Uniform(name="b", lower=0, upper=1, shape=beta_len)


            sim = pm.Simulator("sim", simulation_func, alpha, beta,
                            epsilon=10, observed=data)
            
            idata = pm.sample_smc()

        return idata, data, simulation_func

        # TODO: выташить число людей

        # def simulation_func(rng, alpha, beta, size=None):
        #     self.simulate(
        #         alpha=alpha, 
        #         beta=beta, 
        #         initial_infectious=self.initial_infectious, 
        #         rho=5e5, 
        #         modeling_duration=int(len(data))
        #     )
        #     return self.get_newly_infected()
        
        # with pm.Model() as model:
        #     alpha = pm.Uniform(name="a", lower=0, upper=1)
        #     beta = pm.Uniform(name="b", lower=0, upper=1)


        #     sim = pm.Simulator("sim", simulation_func, alpha, beta,
        #                     epsilon=10, observed=data)
            
        #     idata = pm.sample_smc()

        idata = self.Model.context_manager(self.initial_infectious, data)

        return idata, data
