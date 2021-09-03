import json
from os import stat
import numpy as np
import pandas as pd
from utils import data_reader
from utils import singleton

from hwpc.names import Names


class ModelData(singleton.Singleton):

    data = dict()
    np_data = dict()

    primary_product_to_timber_product = dict()
    end_use_to_timber_product = dict()
    end_use_to_primary_product = dict()

    def __init__(self) -> None:
        super().__init__()
        Names()
        Names().Tables()
        Names().Fields()
        
        self.load_data()
        self.prep_data() 

        self._primary_product_to_timber_product()
        self._end_use_to_timber_product()
        self._end_use_to_primary_product()

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

    @staticmethod
    def get_region_id(region: str) -> int:
        """Get the region ID from a string value.
        TODO add checking for valid string

        Args:
            region (str): The region to lookup

        Returns:
            int: A numeric ID for the region
        """
        regions = ModelData.data[Names.Tables.regions]
        match_region = regions.loc[regions[Names.Fields.region_name] == region][Names.Fields.id].iloc[0]
        return match_region

    @staticmethod
    def _primary_product_to_timber_product():
        ids = ModelData.data[Names.Tables.ids][[Names.Fields.primary_product_id, Names.Fields.timber_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[Names.Fields.primary_product_id]
        values = ids_dict[Names.Fields.timber_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.primary_product_to_timber_product = ids_dict

    @staticmethod
    def __primary_product_to_timber_product(primary_product: int) -> int:
        ids = ModelData.data[Names.Tables.ids]
        timber_id = ids.loc[ids[Names.Fields.primary_product_id] == primary_product][Names.Fields.timber_product_id].iloc[0]
        return timber_id

    @staticmethod
    def _end_use_to_timber_product():
        ids = ModelData.data[Names.Tables.ids][[Names.Fields.end_use_id, Names.Fields.timber_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[Names.Fields.end_use_id]
        values = ids_dict[Names.Fields.timber_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_timber_product = ids_dict

    @staticmethod
    def __end_use_to_timber_product(end_use: int) -> int:
        ids = ModelData.data[Names.Tables.ids]
        timber_id = ids.loc[ids[Names.Fields.end_use_id] == end_use][Names.Fields.timber_product_id].iloc[0]
        return timber_id

    @staticmethod
    def _end_use_to_primary_product():
        ids = ModelData.data[Names.Tables.ids][[Names.Fields.end_use_id, Names.Fields.primary_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[Names.Fields.end_use_id]
        values = ids_dict[Names.Fields.primary_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_primary_product = ids_dict

    @staticmethod
    def __end_use_to_primary_product(primary_product: int) -> int:
        ids = ModelData.data[Names.Tables.ids]
        end_use_id = ids.loc[ids[Names.Fields.primary_product_id] == primary_product][Names.Fields.end_use_id].iloc[0]
        return end_use_id