import json
import pandas as pd
from pandas.core.frame import DataFrame
from utils import data_reader


class ModelData(object):
    
    _instance = None

    data = dict()

    def __new__(cls, *args, **kwargs):
        """Singleton catcher

        Returns:
            ModelData: The singleton ModelData object
        """
        if cls._instance is None:
            cls._instance = super(ModelData, cls).__new__(cls)

        return cls._instance

    @staticmethod
    def load_data() -> None:
        """Read data into pandas DataFrames
        TODO Right now this just looks at default data
        """
        dr = data_reader.DataReader()

        with open('utils/default_paths.json') as f:
            j = json.load(f)
            for k in j:
                p = j[k]
                ModelData.data[k] = dr.read_file(p)

        return

    @staticmethod
    def prep_data() -> None:
        """TODO This function should do any functions needed to prepare data for use.
        Examples could be sorting years, checking for matching yearly data, ratios summing
        to zero, etc.
        """

        return

    @staticmethod
    def get_harvest_years() -> pd.DataFrame:
        harvest_data = ModelData.data['harvest_data']
        years = harvest_data['Year']
        years.sort_values()
        return years
