import pandas as pd
import matplotlib.pyplot as plt
from dateutil import parser


import os 

class EpidData:
    glob_path = os.path.dirname(os.path.abspath(__file__))
    
    def __new__(self, city, start, end) -> None:
        self.city = city

        start = parser.parse(start)
        end = parser.parse(end)

        self.start_year, self.start_week = start.isocalendar()[:2]
        self.end_year, self.end_week = end.isocalendar()[:2]
        print(self.start_year, self.start_week)
        print(self.end_year, self.end_week)

        EpidData.read_epid_data(self)

        return EpidData.get_wave(self)


    def read_epid_data(self) -> None:
        self.epid_df = pd.read_excel(self.glob_path+f'/../../../epid_data/{self.city}/epid_data.xlsx')
        self.epid_df = self.epid_df.apply(lambda x: x.fillna(0), axis=0)

    # def create_dataframe():
    #     epid_df = pd.DataFrame(columns=['year', 'week_number', 'strain_A(H1N1)pdm09_age_0-14_cases', 
    #                                     'strain_A(H3N2)_age_0-14_cases',
    #                                     'strain_B_age_0-14_cases',
    #                                     'population_age_0-14',
    #                                     'strain_A(H1N1)pdm09_age_15+_cases', 
    #                                     'strain_A(H3N2)_age_15+_cases',
    #                                     'strain_B_age_15+_cases',
    #                                     'population_age_15+'])
    #     # datelist = pd.date_range(start='2010-01', end='2023-12', freq='W').tolist()
    #     # epid_df['date'] = datelist
    #     # epid_df.to_excel('epid_data_spb.xlsx')

    def get_wave(self):
        min_year = min(self.epid_df['year'])

        years_df = self.epid_df[
            (self.epid_df.index>=(self.start_year - min_year)*52 + self.start_week-1) &
            (self.epid_df.index<=(self.end_year - min_year)*52 + self.end_week-1)
        ]

        return years_df