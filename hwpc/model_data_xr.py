import json
from typing import overload
import numpy as np
import pandas as pd
import xarray as xr

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

    ids = None

    paper_val = 0
    wood_val = 0

    ds = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            super().__new__(cls, *args, **kwargs)

            self = cls

            self.load_data()
            self.prep_data()

            self._primary_product_to_timber_product()
            self._end_use_to_timber_product()
            self._end_use_to_primary_product()
            self._set_disposition_halflifes()
            self._set_disposition_halflifes_map()
            self._make_id_lookup()

        return cls._instance

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        return

    def __getstate__(self):
        ret = self.__dict__.copy()
        ret["cls_data"] = ModelData.data
        ret["cls_region"] = ModelData.region

        ret["cls_primary_product_to_timber_product"] = ModelData.primary_product_to_timber_product
        ret["cls_end_use_to_timber_product"] = ModelData.end_use_to_timber_product
        ret["cls_end_use_to_primary_product"] = ModelData.end_use_to_primary_product

        ret["cls_disposition_to_halflife"] = ModelData.disposition_to_halflife

        ret["cls_discard_types_dict"] = ModelData.discard_types_dict

        ret["cls_paper_val"] = ModelData.paper_val
        ret["cls_wood_val"] = ModelData.wood_val

        return ret

    def __setstate__(self, state):
        """[summary]

        Args:
            state ([type]): [description]
        """
        ModelData.data = state.pop("cls_data")
        ModelData.region = state.pop("cls_region")

        ModelData.primary_product_to_timber_product = state.pop("cls_primary_product_to_timber_product")
        ModelData.end_use_to_timber_product = state.pop("cls_end_use_to_timber_product")
        ModelData.end_use_to_primary_product = state.pop("cls_end_use_to_primary_product")

        ModelData.disposition_to_halflife = state.pop("cls_disposition_to_halflife")

        ModelData.discard_types_dict = state.pop("cls_discard_types_dict")

        ModelData.paper_val = state.pop("cls_paper_val")
        ModelData.wood_val = state.pop("cls_wood_val")

        self.__dict__.update(state)

    @staticmethod
    def load_data() -> None:
        """Read data into pandas DataFrames
        TODO Right now this just looks at default data
        """
        with open("data/inputs.json") as f:
            j = json.load(f)
            for k in j:
                no_csv = k.replace(".csv", "")
                p = j[k]
                # if no_csv == nm.Tables.harvest:
                #     ks = {nm.Fields.harvest_year: "int16"}
                ModelData.data[no_csv] = pd.read_csv(p)

        return

    @staticmethod
    def prep_data() -> None:
        """TODO This function should do any functions needed to prepare data for use.
        Examples could be sorting years, checking for matching yearly data, ratios summing
        to zero, etc.
        TODO lots of repeated code here... could probably improve this
        """
        df = ModelData.data[nm.Tables.harvest]
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.ccf] = df[nm.Fields.ccf].astype("float32")
        # Add a year to account for the model shift
        max_year = df[nm.Fields.harvest_year].max() + 1
        mf = pd.DataFrame([[max_year, 0.0]], columns=df.columns)
        for x in df.columns:
            mf[x] = mf[x].astype(df[x].dtypes.name)
        df = pd.concat([df, mf])
        df = df.set_index([df[nm.Fields.harvest_year]], drop=True)
        df = df.sort_index()
        df.index = pd.to_numeric(df.index, downcast="integer")
        dx = df.to_xarray()

        # Limit data here for testing
        dx = dx.where(dx.coords[nm.Fields.harvest_year] > 2005, drop=True)
        filtr = dx.coords[nm.Fields.harvest_year].values

        ModelData.data[nm.Tables.harvest] = dx

        # TODO does this work?
        if ModelData.data[nm.Tables.harvest_data_type].columns.values[0] == "mbf":
            ModelData._get_mbf_conversion()

        df = ModelData.data[nm.Tables.timber_products_ratios]
        

        df = ModelData.data[nm.Tables.primary_products]
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype("uint8")
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype("uint8")
        df[nm.Fields.conversion_factor] = df[nm.Fields.conversion_factor].astype("float16")
        df[nm.Fields.ratio_group] = df[nm.Fields.ratio_group].astype("uint8")
        df[nm.Fields.fuel] = df[nm.Fields.fuel].astype("uint8")
        df = df.set_index([nm.Fields.primary_product_id])
        dx = df.to_xarray()
        ModelData.data[nm.Tables.primary_products] = dx

        df = ModelData.data[nm.Tables.end_use_product_ratios]
        df[nm.Fields.end_use_id] = df[nm.Fields.end_use_id].astype("uint8")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.end_use_ratio] = df[nm.Fields.end_use_ratio].astype("float16")
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.end_use_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.end_use_product_ratios] = dx

        df = ModelData.data[nm.Tables.end_use_products]
        df[nm.Fields.end_use_id] = df[nm.Fields.end_use_id].astype("uint8")
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype("uint8")
        df[nm.Fields.end_use_halflife] = df[nm.Fields.end_use_halflife].astype("float32")
        df[nm.Fields.ratio_group] = df[nm.Fields.ratio_group].astype("uint8")
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype("uint8")
        df[nm.Fields.fuel] = df[nm.Fields.fuel].astype("uint8")
        df = df.set_index([nm.Fields.end_use_id])
        dx = df.to_xarray()
        ModelData.data[nm.Tables.end_use_products] = dx

        df = ModelData.data[nm.Tables.discard_destination_ratios]
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype("uint8")
        df[nm.Fields.discard_destination_id] = df[nm.Fields.discard_destination_id].astype("uint8")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.discard_destination_ratio] = df[nm.Fields.discard_destination_ratio].astype("float16")
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.discard_type_id, nm.Fields.discard_destination_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.discard_destination_ratios] = dx

        ModelData.data["pre_" + nm.Tables.timber_products_ratios] = ModelData.data[nm.Tables.timber_products_ratios]

        # Melt the timber_product_data table to make years rows
        try:
            df = ModelData.data[nm.Tables.timber_products_ratios].melt(
                id_vars=nm.Fields.timber_product_id,
                var_name=nm.Fields.harvest_year,
                value_name=nm.Fields.timber_product_ratio,
            )
        except:
            ModelData.data[nm.Tables.timber_products_ratios] = ModelData.data[nm.Tables.timber_products_ratios].rename(
                columns={"Timber Product ID": nm.Fields.timber_product_id}
            )
            df = ModelData.data[nm.Tables.timber_products_ratios].melt(
                id_vars=nm.Fields.timber_product_id,
                var_name=nm.Fields.harvest_year,
                value_name=nm.Fields.timber_product_ratio,
            )

        # Just in case the year was read as a string, parse to numeric
        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year], downcast="integer")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype("uint8")
        df[nm.Fields.timber_product_ratio] = df[nm.Fields.timber_product_ratio].astype("float16")
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.timber_product_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.timber_products_ratios] = dx

        # Parse the region and attempt to pull in default data
        region = ModelData.data[nm.Tables.region].columns[0]
        region_match = ModelData.get_region_id(region)

        if region_match:
            df = ModelData.data[nm.Tables.primary_product_ratios]
            ModelData.data[nm.Tables.primary_product_ratios] = df[df[nm.Fields.region_id] == region_match]
        else:
            # Melt the primary_product_data table to make years rows
            try:
                df = ModelData.data[nm.Tables.primary_product_data].melt(
                    id_vars=nm.Fields.primary_product_id,
                    var_name=nm.Fields.harvest_year,
                    value_name=nm.Fields.ratio,
                )
            except:
                ModelData.data[nm.Tables.primary_product_data] = ModelData.data[
                    nm.Tables.primary_product_data
                ].rename(columns={"Primary Product ID": nm.Fields.primary_product_id})
                df = ModelData.data[nm.Tables.primary_product_data].melt(
                    id_vars=nm.Fields.primary_product_id,
                    var_name=nm.Fields.harvest_year,
                    value_name=nm.Fields.ratio,
                )

        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year])
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype("uint8")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.primary_product_ratio] = df[nm.Fields.primary_product_ratio].astype("float16")
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.primary_product_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.primary_product_ratios] = dx

        conversion = ModelData.data[nm.Tables.ccf_c_conversion][
            [nm.Fields.primary_product_id, nm.Fields.conversion_factor]
        ]

        conversion = conversion.set_index([nm.Fields.primary_product_id])
        conversion.index = pd.to_numeric(conversion.index, downcast="integer")
        conversion[nm.Fields.conversion_factor] = conversion[nm.Fields.conversion_factor].astype("float32")
        xoversion = conversion.to_xarray()
        ModelData.data[nm.Tables.ccf_c_conversion] = xoversion

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

    def _get_mbf_conversion():
        """Expands mbf_to_ccf_conversion.csv from small number of years to ratio per year"""
        # TODO this needs to be updated to xarray
        year_group = {}
        ModelData.data[nm.Tables.mbf_conversion] = pd.read_csv("data/mbf_to_ccf_conversion.csv")

        for i in range(ModelData.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].size):
            year_set = []

            if i < ModelData.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].size - 1:
                for j in range(
                    ModelData.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].values[i],
                    ModelData.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].values[i + 1],
                ):
                    year_set.append(j)
            else:
                for j in range(
                    ModelData.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].values[i],
                    ModelData.data[nm.Tables.harvest][nm.Fields.harvest_year].max(),
                ):
                    year_set.append(j)

            year_set = tuple(year_set)
            year_group[i] = year_set, ModelData.data[nm.Tables.mbf_conversion][nm.Fields.conversion_factor].values[i]

        temp = pd.DataFrame.from_dict(
            year_group,
            orient="index",
            columns=[nm.Fields.harvest_year, nm.Fields.conversion_factor],
        )
        temp = temp.explode(nm.Fields.harvest_year).reset_index(drop=True)

        ModelData.data[nm.Tables.harvest] = ModelData.data[nm.Tables.harvest].merge(
            temp, on=nm.Fields.harvest_year, how="inner"
        )
        ModelData.data[nm.Tables.harvest][nm.Fields.ccf] = (
            ModelData.data[nm.Tables.harvest][nm.Fields.mbf]
            * ModelData.data[nm.Tables.harvest][nm.Fields.conversion_factor]
        )

        return

    @staticmethod
    def _primary_product_to_timber_product():
        ids = ModelData.data[nm.Tables.ids][[nm.Fields.primary_product_id, nm.Fields.timber_product_id]]
        ids_dict = ids.to_dict(orient="list")
        keys = ids_dict[nm.Fields.primary_product_id]
        values = ids_dict[nm.Fields.timber_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.primary_product_to_timber_product = ids_dict
        return

    @staticmethod
    def _end_use_to_timber_product():
        ids = ModelData.data[nm.Tables.ids][[nm.Fields.end_use_id, nm.Fields.timber_product_id]]
        ids_dict = ids.to_dict(orient="list")
        keys = ids_dict[nm.Fields.end_use_id]
        values = ids_dict[nm.Fields.timber_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_timber_product = ids_dict
        return

    @staticmethod
    def _end_use_to_primary_product():
        ids = ModelData.data[nm.Tables.ids][[nm.Fields.end_use_id, nm.Fields.primary_product_id]]
        ids_dict = ids.to_dict(orient="list")
        keys = ids_dict[nm.Fields.end_use_id]
        values = ids_dict[nm.Fields.primary_product_id]
        ids_dict = dict(zip(keys, values))
        ModelData.end_use_to_primary_product = ids_dict
        return

    @staticmethod
    def _make_id_lookup():
        df = ModelData.data[nm.Tables.ids]
        df = df.set_index([nm.Fields.timber_product_id, nm.Fields.primary_product_id, nm.Fields.end_use_id])
        # df = df.set_index([nm.Fields.end_use_id])
        dx = df.to_xarray()
        ModelData.ids = dx

        return

    @staticmethod
    def _set_disposition_halflifes():
        halflifes = ModelData.data[nm.Tables.discard_types]
        vals = halflifes.to_dict(orient="list")

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
        df = ModelData.data[nm.Tables.discard_destinations][
            [nm.Fields.discard_destination_id, nm.Fields.paper_halflife]
        ]
        dat = df.to_dict(orient="list")
        ModelData.disposition_to_halflife[nm.Fields.paper] = dict(
            zip(dat[nm.Fields.discard_destination_id], dat[nm.Fields.paper_halflife])
        )

        df = ModelData.data[nm.Tables.discard_destinations][[nm.Fields.discard_destination_id, nm.Fields.wood_halflife]]
        dat = df.to_dict(orient="list")
        ModelData.disposition_to_halflife[nm.Fields.wood] = dict(
            zip(dat[nm.Fields.discard_destination_id], dat[nm.Fields.wood_halflife])
        )
