import re
from datetime import datetime

import numpy as np
import pandas as pd

pd.options.mode.copy_on_write = True

# TODO: remove dicts from global namespace
cases_table_from_dict_to_excel = {
    "date": "Дата",
    "sars_total_cases": "Всего_орви",
    "sars_cases_age_group_0": "0 - 2_орви",
    "sars_cases_age_group_1": "3 - 6_орви",
    "sars_cases_age_group_2": "7 - 14_орви",
    "sars_cases_age_group_3": "15 и ст._орви",
    "total_population": "Всего",
    "population_age_group_0": "0 - 2",
    "population_age_group_1": "3 - 6",
    "population_age_group_2": "7 - 14",
    "population_age_group_3": "15 и ст.",
}

pcr_table_from_excel_to_python = {
    "date": "Дата",
    "tested_total": "Число образцов тестированных на грипп",
    "tested_strain_0": "A (субтип не определен)",
    "tested_strain_1": "A(H1)pdm09",
    "tested_strain_2": "A(H3)",
    "tested_strain_3": "B",
}


def date_extract(input_string):
    matching = re.search(r"(\d{2}\.\d{2}\.\d{4})", input_string)
    if matching:
        date_string = matching.group(1)
        date_object = datetime.strptime(date_string, "%d.%m.%Y")
        return date_object
    else:
        raise Exception("Incorrect date format!")


class EpidData:
    """
    EpidData class

    Download epidemiological data from excel file
    """

    REGIME_TOTAL = "total"
    REGIME_AGE = "age"
    REGIME_STRAIN = "strain"

    def __init__(self, city: str, path: str, start_time: str, end_time: str) -> None:
        """
        EpidData class

        Download epidemiological data from excel file

        :param city: Name of city
        :param path: path to directory 'data'
        :param start: Start date for extraction
            String of the form "mm-dd-yy"
        :param end: End date for extraction
            String of the form "mm-dd-yy"
        :param type: Name of type. Allowed strings: 'total', 'age', 'strain'.
        """
        self.strain_dict = {
            "A (субтип не определен)": 0,
            "A(H1)pdm09": 1,
            "A(H3)": 2,
            "B": 3,
        }
        self.strain_dict = {
            "A (субтип не определен)": 0,
            "A(H1)pdm09": 1,
            "A(H3)": 2,
            "B": 3,
        }
        self.strains_number = 4
        self.cases_df = None
        self.pcr_df = None
        self.returned_df = None

        self.start_time = datetime.strptime(start_time, "%d-%m-%Y")
        self.end_time = datetime.strptime(end_time, "%d-%m-%Y")
        self.data_folder = path.rstrip("/") + f"/data/{city}/"

        self.__read_all_data()

    def __read_all_data(self) -> None:
        """
        Download all data from folder
        :return:
        """
        # read cases.xlsx file
        self.cases_df = self.__data_to_dataframe(
            "cases.xlsx", cases_table_from_dict_to_excel
        )

        # read pcr.xlsx file
        self.pcr_df = self.__data_to_dataframe("pcr.xlsx", pcr_table_from_excel_to_python)

        for strain_index in range(self.strains_number):
            str_ind = str(strain_index)
            self.cases_df["rel_strain_" + str_ind] = (
                self.pcr_df["tested_strain_" + str_ind] / self.pcr_df["tested_total"]
            )
            self.cases_df["real_cases_strain_" + str_ind] = (
                self.cases_df["rel_strain_" + str_ind] * self.cases_df["sars_total_cases"]
            ).round()

    def __data_to_dataframe(self, file: str, table: dict[str, str]) -> pd.DataFrame:
        """
        Download excel file from data folder

        :param file: Name of excel file
        :param table: Table header

        :return: Excel file in DataFrame format
        """
        excel_file = pd.read_excel(self.data_folder + file)
        df = pd.DataFrame(columns=table.keys())

        for col_name in df.columns:
            df[col_name] = excel_file[table[col_name]]

        df["datetime"] = df["date"].apply(date_extract)

        return df.fillna(float("nan"))

    def __get_time_period(self) -> None:
        """
        Get data from the desired time interval
        :return:
        """
        self.returned_df = self.cases_df[
            (self.cases_df["datetime"] > self.start_time)
            & (self.cases_df["datetime"] < self.end_time)
        ]

    def __transform_data_for_type(self, type: str) -> None:
        """
        Transform data for each type

        :param type: Name of type

        :return:
        """
        # TODO: think about nan values. In epidemic data nan != 0.
        # That is why using method fillna(0) is slightly incorrect.
        self.returned_df["total_cases"] = self.returned_df.fillna(0)[
            ["real_cases_strain_1", "real_cases_strain_2", "real_cases_strain_3"]
        ].sum(axis=1)

        if type == self.REGIME_TOTAL:
            self.returned_df = self.returned_df[
                ["datetime", "total_cases", "total_population"]
            ]

        elif type == self.REGIME_AGE:
            # sum up cases from age groups: 0-2, 3-6, 7-14
            # because we work with 0-14 and 15+
            # TODO: think about nan values. In epidemic data nan != 0.
            self.returned_df["sars_cases_age_group_0-2"] = self.returned_df.fillna(0)[
                [
                    "sars_cases_age_group_0",
                    "sars_cases_age_group_1",
                    "sars_cases_age_group_2",
                ]
            ].sum(axis=1)

            rel_cases_age_group_0_2 = (
                self.returned_df["sars_cases_age_group_0-2"]
                / self.returned_df["sars_total_cases"]
            )

            rel_cases_age_group_3 = (
                self.returned_df["sars_cases_age_group_3"]
                / self.returned_df["sars_total_cases"]
            )

            # check if the sum of relative diseases is not equal to 1
            to_assert = -1 + abs(
                rel_cases_age_group_0_2.iloc[1] + rel_cases_age_group_3.iloc[1]
            )

            assert to_assert < 1e-5

            # final calculated cases
            self.returned_df["age_group_0-2_cases"] = (
                rel_cases_age_group_0_2 * self.returned_df["total_cases"]
            )
            self.returned_df["age_group_3_cases"] = (
                rel_cases_age_group_3 * self.returned_df["total_cases"]
            )

            self.returned_df = self.returned_df[
                [
                    "datetime",
                    "age_group_0-2_cases",
                    "age_group_3_cases",
                    "total_population",
                ]
            ]

    def __set_timedelta(self):
        deltatime = self.returned_df["datetime"]
        deltadays = (deltatime.iloc[1] - deltatime.iloc[0]).days

        self.returned_df.attrs = {"time_step": "week" if deltadays == 7 else "day"}

    def get_wave_data(self, type: str) -> pd.DataFrame:
        """
        Obtaining data for the epidemiological wave

        :param type: Name of type

        :return: Epidemiological wave
        """
        self.__get_time_period()
        assert isinstance(self.returned_df, pd.DataFrame)
        self.__transform_data_for_type(type)
        self.__set_timedelta()

        return self.returned_df

    def get_rho(self) -> int:
        """
        Get number of people in population
        :return: Number of people
        """
        return self.returned_df["total_population"].iloc[0]

    def prepare_for_plot(self) -> np.array:
        """
        Obtaining data in graphing format
        :return: Plot data
        """
        return np.array(self.returned_df.drop(columns=["datetime", "total_population"]))

    def get_data(self) -> np.array:
        """
        Obtaining data for calibration
        :return: Data for calibration
        """
        return self.returned_df.drop(columns=["total_population"])

    def get_duration(self) -> int:
        return (
            len(self.returned_df) * 7
            if self.returned_df.attrs["time_step"] == "week"
            else len(self.returned_df)
        )
