import pandas as pd
from dateutil import parser


class EpidData:
    def __new__(
        self, 
        city: str, 
        path: str,
        start: str, 
        end: str,
    ) -> pd.DataFrame:
        """
        EpidData class

        Download epidemiological excel data file from the subdirectory of epid_data.
        epid_data directory looks like 'epid_data/{city}/epid_data.xlsx'.

        :param city: Name of city  
        :param path: path to directory 'epid_data'
        :param start: First day of extracted data
            String of the form "mm-dd-yy"
        :param end: Last day of extracted data
            String of the form "mm-dd-yy"

        :return: Extracted data in the desired interval
        """
        start = parser.parse(start)
        end = parser.parse(end)

        self.start = start
        self.city = city
        self.path = path
        self.start_year, self.start_week = start.isocalendar()[:2]
        self.end_year, self.end_week = end.isocalendar()[:2]

        EpidData.__read_epid_data(self)
        EpidData.__get_wave(self)
        EpidData.__preprocess_wave(self)

        return self.epid_df


    def __read_epid_data(self) -> None:
        """
        Download excel file from epid_data folder

        :return: 
        """

        self.epid_df = pd.read_excel(
            self.path.rstrip('/') + f'/data/{self.city}/epid_data.xlsx'
        )
        self.epid_df = self.epid_df.apply(lambda x: x.fillna(float('nan')), axis=0)


    def __get_wave(self) -> None:
        """
        Select the desired interval

        :return:
        """

        min_year = min(self.epid_df['year'])
        self.epid_df = self.epid_df[
            (self.epid_df.index >= (self.start_year - min_year) * 52 + self.start_week - 1) &
            (self.epid_df.index <= (self.end_year - min_year) * 52 + self.end_week - 1)
        ]

    
    def __preprocess_wave(self) -> None:
        """
        Change time stamp

        :return:
        """
                
        start = pd.to_datetime(self.start)
        self.epid_df['date'] = pd.date_range(start, periods=len(self.epid_df), freq='W')
        self.epid_df = self.epid_df.drop(['week_number', 'year'], axis=1)