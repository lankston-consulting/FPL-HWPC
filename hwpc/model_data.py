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

        # TODO move the renaming here from model.py
        # ModelData.data[Names.Tables.timber_products] = ModelData.data[Names.Tables.timber_products].rename(columns={Names.Fields.ratio: Names.Fields.timber_product_ratio})
        # ModelData.data[Names.Tables.primary_product_ratios] = ModelData.data[Names.Tables.primary_product_ratios].rename(columns={Names.Fields.ratio: Names.Fields.primary_product_ratio})
        # ModelData.data[Names.Tables.end_use_ratios] = ModelData.data[Names.Tables.end_use_ratios].rename(columns={Names.Fields.ratio: Names.Fields.end_use_ratio})


        # Prep the harvest data table by sorting years in ascending order
        ModelData.data[Names.Tables.harvest].sort_values(by=[Names.Fields.harvest_year], inplace=True)

        df = ModelData.data[Names.Tables.timber_products].melt(id_vars=Names.Fields.timber_product_id, 
                                                               var_name=Names.Fields.harvest_year, 
                                                               value_name=Names.Fields.ratio)
        
        df[Names.Fields.harvest_year] = pd.to_numeric(df[Names.Fields.harvest_year])
        ModelData.data[Names.Tables.timber_products] = df



        df = ModelData.data[Names.Tables.end_use_halflifes]
        df = df.rename(columns={Names.Fields.id: Names.Fields.end_use_id})
        ModelData.data[Names.Tables.end_use_halflifes] = df
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
    def _end_use_to_timber_product():
        ids = ModelData.data[Names.Tables.ids][[Names.Fields.end_use_id, Names.Fields.timber_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[Names.Fields.end_use_id]
        values = ids_dict[Names.Fields.timber_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_timber_product = ids_dict

    @staticmethod
    def _end_use_to_primary_product():
        ids = ModelData.data[Names.Tables.ids][[Names.Fields.end_use_id, Names.Fields.primary_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[Names.Fields.end_use_id]
        values = ids_dict[Names.Fields.primary_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_primary_product = ids_dict
