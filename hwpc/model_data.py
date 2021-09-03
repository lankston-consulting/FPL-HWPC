import json
import numpy as np
import pandas as pd
from utils import data_reader
from utils import singleton

from hwpc.names import Names


class ModelData(singleton.Singleton):

    data = dict()
    np_data = dict()

    def __init__(self) -> None:
        super().__init__()
        Names()
        Names().Tables()
        Names().Fields()

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

        # Prep the harvest data table by sorting years in ascending order
        ModelData.data[Names.Tables.harvest].sort_values(by=[Names.Fields.harvest_year], inplace=True)

        df = ModelData.data[Names.Tables.timber_products].melt(id_vars=Names.Fields.timber_product_id, 
                                                               var_name=Names.Fields.harvest_year, 
                                                               value_name=Names.Fields.ratio)
        
        df[Names.Fields.harvest_year] = pd.to_numeric(df[Names.Fields.harvest_year])
        ModelData.data[Names.Tables.timber_products] = df

        # print(df.head())
        # print(df.tail())
        return

    @staticmethod
    def get_harvest_years() -> pd.DataFrame:
        harvest_data = ModelData.data[Names.Tables.harvest]
        years = harvest_data[Names.Fields.harvest_year]
        years = years.sort_values()
        return years
