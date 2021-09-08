import json
from os import stat
import numpy as np
import pandas as pd
from utils import data_reader
from utils import singleton

from hwpc.names import Names as nm


class ModelData(singleton.Singleton):

    data = dict()
    np_data = dict()

    primary_product_to_timber_product = dict()
    end_use_to_timber_product = dict()
    end_use_to_primary_product = dict()

    disposition_to_halflife = dict()

    discard_types_dict = dict()

    paper_val = 0
    wood_val = 0

    def __init__(self) -> None:
        super().__init__()
        nm()
        nm().Tables()
        nm().Fields()
        
        self.load_data()
        self.prep_data() 

        self._primary_product_to_timber_product()
        self._end_use_to_timber_product()
        self._end_use_to_primary_product()
        self._set_disposition_halflifes()
        self._set_disposition_halflifes_map()

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
        # ModelData.data[nm.Tables.timber_products] = ModelData.data[nm.Tables.timber_products].rename(columns={nm.Fields.ratio: nm.Fields.timber_product_ratio})
        # ModelData.data[nm.Tables.primary_product_ratios] = ModelData.data[nm.Tables.primary_product_ratios].rename(columns={nm.Fields.ratio: nm.Fields.primary_product_ratio})
        # ModelData.data[nm.Tables.end_use_ratios] = ModelData.data[nm.Tables.end_use_ratios].rename(columns={nm.Fields.ratio: nm.Fields.end_use_ratio})


        # Prep the harvest data table by sorting years in ascending order
        ModelData.data[nm.Tables.harvest].sort_values(by=[nm.Fields.harvest_year], inplace=True)

        df = ModelData.data[nm.Tables.timber_products].melt(id_vars=nm.Fields.timber_product_id, 
                                                               var_name=nm.Fields.harvest_year, 
                                                               value_name=nm.Fields.ratio)
        
        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year])
        ModelData.data[nm.Tables.timber_products] = df



        df = ModelData.data[nm.Tables.end_use_halflifes]
        df = df.rename(columns={nm.Fields.id: nm.Fields.end_use_id})
        ModelData.data[nm.Tables.end_use_halflifes] = df
        return

    @staticmethod
    def get_harvest_years() -> pd.DataFrame:
        harvest_data = ModelData.data[nm.Tables.harvest]
        years = harvest_data[nm.Fields.harvest_year]
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
        regions = ModelData.data[nm.Tables.regions]
        match_region = regions.loc[regions[nm.Fields.region_name] == region][nm.Fields.id].iloc[0]
        return match_region

    @staticmethod
    def _primary_product_to_timber_product():
        ids = ModelData.data[nm.Tables.ids][[nm.Fields.primary_product_id, nm.Fields.timber_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[nm.Fields.primary_product_id]
        values = ids_dict[nm.Fields.timber_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.primary_product_to_timber_product = ids_dict

    @staticmethod
    def _end_use_to_timber_product():
        ids = ModelData.data[nm.Tables.ids][[nm.Fields.end_use_id, nm.Fields.timber_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[nm.Fields.end_use_id]
        values = ids_dict[nm.Fields.timber_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_timber_product = ids_dict

    @staticmethod
    def _end_use_to_primary_product():
        ids = ModelData.data[nm.Tables.ids][[nm.Fields.end_use_id, nm.Fields.primary_product_id]]
        ids_dict = ids.to_dict(orient='list')
        keys = ids_dict[nm.Fields.end_use_id]
        values = ids_dict[nm.Fields.primary_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_primary_product = ids_dict

    @staticmethod
    def _set_disposition_halflifes():
        halflifes = ModelData.data[nm.Tables.discard_types]
        vals = halflifes.to_dict(orient='list')

        paper_i = vals[nm.Fields.discard_description].index(nm.Fields.paper)
        wood_i = vals[nm.Fields.discard_description].index(nm.Fields.wood)

        ModelData.paper_val = paper_i
        ModelData.wood_val = wood_i

        ModelData.discard_types_dict = {nm.Fields.paper: dict(), nm.Fields.wood: dict()}

        for k in vals:
            ModelData.discard_types_dict[nm.Fields.paper][k] = vals[k][paper_i]
            ModelData.discard_types_dict[nm.Fields.wood][k] = vals[k][wood_i]

    @staticmethod
    def _set_disposition_halflifes_map():
        df = ModelData.data[nm.Tables.discard_destinations][[nm.Fields.discard_destination_id, nm.Fields.paper_halflife]]
        dat = df.to_dict(orient='list')
        ModelData.disposition_to_halflife[nm.Fields.paper] = dict(zip(dat[nm.Fields.discard_destination_id], dat[nm.Fields.paper_halflife]))
        
        df = ModelData.data[nm.Tables.discard_destinations][[nm.Fields.discard_destination_id, nm.Fields.wood_halflife]]
        dat = df.to_dict(orient='list')
        ModelData.disposition_to_halflife[nm.Fields.wood] = dict(zip(dat[nm.Fields.discard_destination_id], dat[nm.Fields.wood_halflife]))