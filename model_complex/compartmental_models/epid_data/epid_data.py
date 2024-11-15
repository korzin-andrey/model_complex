import pandas as pd
from dateutil import parser
import re
import datetime
import numpy as np

# TODO: remove dicts from global namespace
cases_table_from_dict_to_excel = {
                    'date': 'Дата',
                    'sars_total_cases': 'Всего_орви',
                    'sars_cases_age_group_0': '0 - 2_орви',
                    'sars_cases_age_group_1': '3 - 6_орви',
                    'sars_cases_age_group_2': '7 - 14_орви',
                    'sars_cases_age_group_3': '15 и ст._орви',
                    'total_population': 'Всего',
                    'population_age_group_0': '0 - 2',
                    'population_age_group_1': '3 - 6',
                    'population_age_group_2': '7 - 14',
                    'population_age_group_3': '15 и ст.',
                    }

pcr_table_from_excel_to_python = {'date': 'Дата',
                                  'tested_total': 'Число образцов тестированных на грипп',
                                  'tested_strain_0': 'A (субтип не определен)',
                                  'tested_strain_1': 'A(H1)pdm09',
                                  'tested_strain_2': 'A(H3)',
                                  'tested_strain_3': 'B'
                                  }


def date_extract(input_string):
    matching = re.search(r'(\d{2}\.\d{2}\.\d{4})', input_string)
    if matching:
        date_string = matching.group(1)
        date_object = datetime.datetime.strptime(date_string, "%d.%m.%Y")
        return date_object
    else:
        raise Exception("Incorrect date format!")

class EpidData:
    def __init__(
        self, 
        city: str, 
        path: str,
        start_time: str, 
        end_time: str,
        regime: str
    ):
        """
        EpidData class

        Download epidemiological excel data file from the subdirectory of epid_data.
        epid_data directory looks like 'epid_data/{city}/epid_data.xlsx'.

        :param city: Name of city  
        :param path: path to directory 'epid_data'
        :param start: Start date for extraction
            String of the form "mm-dd-yy"
        :param end: End date for extraction
            String of the form "mm-dd-yy"
        :param strain: Name of strain. See strain_dict for strain names.
        """
        self.strain_dict = {'A (субтип не определен)': 0,
                            'A(H1)pdm09': 1,
                            'A(H3)': 2, 'B': 3
                            }
        self.regime = regime
        self.start_time = datetime.datetime.strptime(start_time, "%d-%m-%Y")
        self.end_time = datetime.datetime.strptime(end_time, "%d-%m-%Y")
        self.city = city
        self.path = path
        self.strains_number = 4
        self.cases_df = None
        self.pcr_df = None

    def __read_epid_data_to_dataframe(self) -> None:
        """
        Download excel file from epid_data folder
        :return: 
        """
        # read cases.xlsx file
        excel_file_cases = pd.read_excel(self.path.rstrip('/') + 
                                         f'/data/{self.city}/cases.xlsx')
        self.cases_df = pd.DataFrame(columns=cases_table_from_dict_to_excel.keys())
        for col_name in self.cases_df.columns:
            self.cases_df[col_name] = excel_file_cases[cases_table_from_dict_to_excel[col_name]]
        self.cases_df['datetime'] = self.cases_df['date'].apply(date_extract)
        self.cases_df = self.cases_df.fillna(float('nan'))
        
        # read pcr.xlsx file
        excel_file_pcr = pd.read_excel(self.path.rstrip('/') + f'/data/{self.city}/pcr.xlsx')
        self.pcr_df = pd.DataFrame(columns=pcr_table_from_excel_to_python.keys())
        for col_name in self.pcr_df.columns:
            self.pcr_df[col_name] = excel_file_pcr[pcr_table_from_excel_to_python[col_name]]
        self.pcr_df['datetime'] = self.pcr_df['date'].apply(date_extract)
        self.pcr_df = self.pcr_df.fillna(float('nan'))
        for strain_index in range(self.strains_number):
            str_ind = str(strain_index)
            self.cases_df['rel_strain_' + str_ind] = self.pcr_df['tested_strain_' + str_ind]/self.pcr_df['tested_total']
            self.cases_df['real_cases_strain_' + str_ind] = (self.cases_df['rel_strain_' + str_ind]*self.cases_df['sars_total_cases']).round()


    def __get_time_period(self) -> None:
        """
        Get data from the desired time interval
        :return:
        """ 
        self.cases_df = self.cases_df[(self.cases_df['datetime'] > self.start_time) &
                                      (self.cases_df['datetime'] < self.end_time)]


    def __transform_data_for_regime(self) -> None:
        if self.regime == 'total':
            # TODO: think about nan values. In epidemic data nan != 0.
            self.cases_df['total_cases'] = self.cases_df.fillna(0)[['real_cases_strain_1', 
                                                               'real_cases_strain_2', 
                                                               'real_cases_strain_3']].sum(axis=1)
            self.cases_df = self.cases_df[['datetime', 'total_cases', 'total_population']]
        if self.regime == 'age':
            raise NotImplementedError
        

    def get_wave_data(self):
        self.__read_epid_data_to_dataframe()
        self.__get_time_period()
        self.__transform_data_for_regime()
        return self.cases_df

        
    def prepare_for_calibration(self):
        return np.array(self.cases_df.drop(columns=['datetime', 'total_population'])).T.flatten()
        