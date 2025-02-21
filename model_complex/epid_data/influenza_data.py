from datetime import datetime
from io import StringIO

import pandas as pd
import requests

from .epid_data import EpidData

pd.options.mode.copy_on_write = True

# TODO: remove dicts from global namespace
table_from_dict = {
    "YEAR": "datetime",
    "REGION_NAME": "region_name",
    "DISTRICT_NAME": "district_name",
    "ARI_TOTAL": "sars_total_cases",
    "ARI_0_2": "sars_cases_age_group_0",
    "ARI_3_6": "sars_cases_age_group_1",
    "ARI_7_14": "sars_cases_age_group_2",
    "ARI_15_64": "sars_cases_age_group_4",
    "ARI_65": "sars_cases_age_group_5",
    "POP_TOTAL": "total_population",
    "POP_0_2": "population_age_group_0",
    "POP_3_6": "population_age_group_1",
    "POP_7_14": "population_age_group_2",
    "POP_15_64": "population_age_group_4",
    "POP_65": "population_age_group_5",
    "SWB_TOTAL": "tested_total",
    "A_TOTAL": "tested_strain_0",
    "PDM_TOTAL": "tested_strain_1",
    "H3_TOTAL": "tested_strain_2",
    "B_TOTAL": "tested_strain_3",
}

# ARI_ - ОРВИ
# POP_ - Население

# SWB_ - Число образцов на грипп
# A_ - Положительные на грипп А (не субтипировано)
# PDM_ - Положительные на грипп H1pdm09
# H3_ - Положительные на грипп H3
# B_ - Положительные на грипп B


def date_creation(input):
    return datetime.strptime(f'{input["YEAR"]}-W{input["WEEK"]}-1', "%G-W%V-%u")


class InfluenzaData(EpidData):
    """
    InfluenzaData class

    Download epidemiological data from https://db.influenza.spb.ru
    """

    city_to_id = {"russia": 0, "spb": 38}

    secret = ""

    url = (
        "https://db.influenza.spb.ru/scripts/report/rmancgi.exe"
        + "?reportname=get_csv&id=aripcr"
        + "&byear={}&bweek={}&eyear={}&eweek={}&district={}&auth={}"
    )

    def __init__(
        self, city: str, begin_year: int, begin_week: int, end_year: int, end_week: int
    ) -> None:

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
        self.df = None
        self.pcr_df = None
        self.returned_df = None

        self.start_time = datetime.strptime(f"{begin_year}-W{begin_week}-1", "%G-W%V-%u")
        self.end_time = datetime.strptime(f"{end_year}-W{end_week}-1", "%G-W%V-%u")

        self.begin_year = begin_year
        self.begin_week = begin_week
        self.end_year = end_year
        self.end_week = end_week
        self.city = city

        self.__read_all_data()

    def __read_all_data(self):
        # получаем данные и декодируем их
        data = requests.get(
            self.url.format(
                self.begin_year,
                self.begin_week,
                self.end_year,
                self.end_week,
                self.city_to_id[self.city.lower()],
                "7e283896cf78e49c321dc60fab2850745a25215b621f600f648424d242a78c4a",
            )
        ).content.decode("utf-8")

        # преобразуем в датафрэйм
        self.cases_df = pd.read_csv(StringIO(data), sep="|")

        # преобразуем в даты
        self.cases_df["YEAR"] = self.cases_df.apply(date_creation, axis=1)

        # оставляем только нужные столбцы
        self.cases_df = self.cases_df.loc[:, list(table_from_dict.keys())]

        # переименовываем столбцы
        self.cases_df = self.cases_df.rename(columns=table_from_dict).fillna(float("nan"))

        # добавляем группу 15+
        self.cases_df["sars_cases_age_group_3"] = (
            self.cases_df["sars_cases_age_group_4"]
            + self.cases_df["sars_cases_age_group_5"]
        )
        self.cases_df["population_age_group_3"] = (
            self.cases_df["population_age_group_4"]
            + self.cases_df["population_age_group_5"]
        )

        # добавляем rel_strain и real_cases_strain
        for strain_index in range(self.strains_number):
            self.cases_df[f"rel_strain_{strain_index}"] = (
                self.cases_df[f"tested_strain_{strain_index}"]
                / self.cases_df["tested_total"]
            )
            self.cases_df[f"real_cases_strain_{strain_index}"] = (
                self.cases_df[f"rel_strain_{strain_index}"]
                * self.cases_df["sars_total_cases"]
            ).round()

        self.cases_df = self.cases_df.drop(
            columns=[
                "tested_total",
                "tested_strain_0",
                "tested_strain_1",
                "tested_strain_2",
                "tested_strain_3",
            ]
        )

        self.cases_df = self.cases_df.fillna(float("nan"))
