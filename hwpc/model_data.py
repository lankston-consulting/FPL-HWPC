import json
import numpy as np
import pandas as pd

from utils import data_reader
from utils import pickler
from utils import singleton

from hwpc.names import Names as nm


class ModelData(pickler.Pickler, singleton.Singleton):

    data = dict()
    region = None

    primary_product_to_timber_product = dict()
    end_use_to_timber_product = dict()
    end_use_to_primary_product = dict()

    disposition_to_halflife = dict()

    discard_types_dict = dict()

    paper_val = 0
    wood_val = 0

    def __init__(self) -> None:
        super().__init__()
        
        self.load_data()
        self.prep_data() 

        self._primary_product_to_timber_product()
        self._end_use_to_timber_product()
        self._end_use_to_primary_product()
        self._set_disposition_halflifes()
        self._set_disposition_halflifes_map()

    def __getstate__(self):
        ret = self.__dict__.copy()
        ret['cls_data'] = ModelData.data
        ret['cls_region'] = ModelData.region

        ret['cls_primary_product_to_timber_product'] = ModelData.primary_product_to_timber_product
        ret['cls_end_use_to_timber_product'] = ModelData.end_use_to_timber_product
        ret['cls_end_use_to_primary_product'] = ModelData.end_use_to_primary_product

        ret['cls_disposition_to_halflife'] = ModelData.disposition_to_halflife

        ret['cls_discard_types_dict'] = ModelData.discard_types_dict

        ret['cls_paper_val'] = ModelData.paper_val
        ret['cls_wood_val'] = ModelData.wood_val

        return ret

    def __setstate__(self, state):
        ModelData.data = state.pop('cls_data')
        ModelData.region = state.pop('cls_region')

        ModelData.primary_product_to_timber_product = state.pop('cls_primary_product_to_timber_product')
        ModelData.end_use_to_timber_product = state.pop('cls_end_use_to_timber_product')
        ModelData.end_use_to_primary_product = state.pop('cls_end_use_to_primary_product')

        ModelData.disposition_to_halflife = state.pop('cls_disposition_to_halflife')

        ModelData.discard_types_dict = state.pop('cls_discard_types_dict')

        ModelData.paper_val = state.pop('cls_paper_val')
        ModelData.wood_val = state.pop('cls_wood_val')

        self.__dict__.update(state)


    @staticmethod
    def load_data() -> None:
        """Read data into pandas DataFrames
        TODO Right now this just looks at default data
        """
        dr = data_reader.DataReader()

        with open('data/inputs.json') as f:
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
        ModelData.data[nm.Tables.primary_product_ratios] = ModelData.data[nm.Tables.primary_product_ratios].rename(columns={nm.Fields.ratio: nm.Fields.primary_product_ratio})

        ModelData.data[nm.Tables.primary_products] = ModelData.data[nm.Tables.primary_products].rename(columns={nm.Fields.id: nm.Fields.primary_product_id})

        ModelData.data[nm.Tables.end_use_ratios] = ModelData.data[nm.Tables.end_use_ratios].rename(columns={nm.Fields.ratio: nm.Fields.end_use_ratio})

        ModelData.data[nm.Tables.end_use_halflifes] = ModelData.data[nm.Tables.end_use_halflifes].rename(columns={nm.Fields.id: nm.Fields.end_use_id})

        ModelData.data[nm.Tables.discard_disposition_ratios] = ModelData.data[nm.Tables.discard_disposition_ratios].rename(columns={nm.Fields.ratio: nm.Fields.discard_destination_ratio})

        # Melt the timber_product_data table to make years rows
        try:
            df = ModelData.data[nm.Tables.timber_products_data].melt(id_vars=nm.Fields.timber_product_id, 
                                                                     var_name=nm.Fields.harvest_year, 
                                                                     value_name=nm.Fields.timber_product_ratio)
        except:
            ModelData.data[nm.Tables.timber_products_data] =  ModelData.data[nm.Tables.timber_products_data].rename(columns={'Timber Product ID': nm.Fields.timber_product_id})
            df = ModelData.data[nm.Tables.timber_products_data].melt(id_vars=nm.Fields.timber_product_id, 
                                                                     var_name=nm.Fields.harvest_year, 
                                                                     value_name=nm.Fields.timber_product_ratio)
        
        # Just in case the year was read as a string, parse to numeric
        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year])
        ModelData.data[nm.Tables.timber_products_data] = df

        # Parse the region and attempt to pull in default data
        region = ModelData.data[nm.Tables.region].columns[0]
        region_match = ModelData.get_region_id(region)

        if region_match:
            df = ModelData.data[nm.Tables.primary_product_ratios] 
            ModelData.data[nm.Tables.primary_product_ratios] = df[df[nm.Fields.id] == region_match]
        else:
            # Melt the primary_product_data table to make years rows
            try:
                df = ModelData.data[nm.Tables.primary_products_data].melt(id_vars=nm.Fields.primary_product_id, 
                                                                        var_name=nm.Fields.harvest_year, 
                                                                        value_name=nm.Fields.ratio)
            except:
                ModelData.data[nm.Tables.primary_products_data] =  ModelData.data[nm.Tables.primary_products_data].rename(columns={'Primary Product ID': nm.Fields.primary_product_id})
                df = ModelData.data[nm.Tables.primary_products_data].melt(id_vars=nm.Fields.primary_product_id, 
                                                                            var_name=nm.Fields.harvest_year, 
                                                                            value_name=nm.Fields.ratio)

            df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year])
            ModelData.data[nm.Tables.primary_product_ratios] = df

        ModelData.data[nm.Tables.primary_product_ratios] = ModelData.data[nm.Tables.primary_product_ratios].rename(columns={nm.Fields.ratio: nm.Fields.primary_product_ratio})

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
        if region in regions[nm.Fields.region_name].unique():
            match_region = regions.loc[regions[nm.Fields.region_name] == region][nm.Fields.id].iloc[0]
        else:
            match_region = None
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