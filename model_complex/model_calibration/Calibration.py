import scipy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymc as pm

from .data_extraction.data_extraction import EpidData

from models import FactoryBRModel

class Calibration:

    def __init__(self, incidence, initial_infectious, people_nums):
        self.BRModel = FactoryBRModel(incidence)
        self.initial_infectious = initial_infectious
        self. people_nums = people_nums
        self.epi = EpidData('spb', '2010-10-02', '2011-10-10')



    # def calibrate(self, city, start, end):
     
    #     def simulation_func(rng, alpha, beta, size=None):
    #         """ Simulation function for use in pm.Simulator """
    #         br_model = self.BRModel(alpha=alpha, beta=beta, initial_infectious=self.initial_infectious, rho=self. people_nums)
    #         br_model.simulate(modeling_duration=season_len)
    #         return br_model.get_newly_infected()

    #     with pm.Model() as model:
    #         alpha = pm.Uniform(name="alpha", lower=0, upper=1)
    #         beta = pm.Uniform(name="beta", lower=0, upper=1)
    #         sim = pm.Simulator("sim", simulation_func, params=(alpha, beta), 
    #                         epsilon=10, observed=data[index])
    #         idata = pm.sample_smc()