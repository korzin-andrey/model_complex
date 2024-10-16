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
        initial_infectious: int,
        people_nums: int,
        ) -> None:
        """
        Calibration class

        TODO

        :param incidence: Name of city  
        :param initial_infectious: Name of city  
        :param people_nums: Name of city  
        """

        self.BRModel = FactoryBRModel.get_model(incidence)
        self.initial_infectious = initial_infectious
        self.people_nums = people_nums


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
        BRModel = self.BRModel
        data = BRModel.data_columns(epid_data)


        def simulation_func(rng, alpha, beta, size=None):
            BRModel.simulate(alpha=alpha, beta=beta, initial_infectious=100, rho=5e5, modeling_duration=len(data))
            return BRModel.get_newly_infected()
        
        with pm.Model() as model:
            alpha = pm.Uniform(name="alpha", lower=0, upper=1)
            beta = pm.Uniform(name="beta", lower=0, upper=1)
            sim = pm.Simulator("sim", simulation_func, params=(alpha, beta), 
                            epsilon=10, observed=data)
            idata = pm.sample_smc()

        return idata, simulation_func, data
