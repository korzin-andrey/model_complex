import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.pyplot as plt

class EpidData:
    def __init__(self) -> None:
        self.epid_df = None
        self.waves = None # list of lists of epidemic waves

    def create_dataframe():
        epid_df = pd.DataFrame(columns=['year', 'week_number', 'strain_A(H1N1)pdm09_age_0-14_cases', 
                                        'strain_A(H3N2)_age_0-14_cases',
                                        'strain_B_age_0-14_cases',
                                        'population_age_0-14',
                                        'strain_A(H1N1)pdm09_age_15+_cases', 
                                        'strain_A(H3N2)_age_15+_cases',
                                        'strain_B_age_15+_cases',
                                        'population_age_15+'])
        # datelist = pd.date_range(start='2010-01', end='2023-12', freq='W').tolist()
        # epid_df['date'] = datelist
        # epid_df.to_excel('epid_data_spb.xlsx')

    def read_epid_data(self, filename='epid_data/epid_data_spb.xlsx'):
        self.epid_df = pd.read_excel(filename)
        self.epid_df.fillna(value=0)

    def get_waves(self):
        incidence = self.epid_df['total'][:-100].to_list()
        self.waves = []
        for i in range(10):
            self.waves.append(incidence[52-25 + 52*i:52+25 + 52*i])
    
    def plot_whole_epid_data(self):
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(self.epid_df['total'][40:-100], '--o')
        ax.grid()
        fig.savefig('incidence.png', bbox_inches='tight')
    
    def plot_waves(self):
        fig, ax = plt.subplots(figsize=(10,5))
        for wave in self.waves:
            ax.plot(wave, '--o', color='royalblue', alpha=0.6)
        ax.grid()
        fig.savefig('waves.png', bbox_inches='tight')

    def save_epid_data(self):
        for index, wave in enumerate(self.waves):
            epid_data = pd.DataFrame(columns=['incidence'])
            epid_data['incidence'] = wave
            epid_data.to_csv(f'epid_data/epid_influenza_season_{index}.csv')


if __name__ == '__main__':
    epid_data = EpidData()
    epid_data.read_epid_data()
    # epid_data.plot_epid_data()
    epid_data.get_waves()
    epid_data.save_epid_data()
    epid_data.plot_waves()