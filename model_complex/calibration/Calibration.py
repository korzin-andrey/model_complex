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

        Model = self.Model
        data = Model.data_columns(epid_data)

        # TODO: выташить число людей


        idata = Model.context_manager(self.initial_infectious, data)

        return idata, data
