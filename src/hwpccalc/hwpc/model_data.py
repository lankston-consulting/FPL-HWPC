import json
import os
from io import BytesIO

import numpy as np
import pandas as pd
import requests
import xarray as xr

import hwpccalc.config
from hwpccalc.hwpc.names import Names as nm
from hwpccalc.utils import pickler, s3_helper

pd.options.mode.chained_assignment = None

_debug_mode = hwpccalc.config._debug_mode

if _debug_mode:
    _debug_start_year = int(os.getenv("HWPC__DEBUG__START_YEAR"))
    _debug_end_year = int(os.getenv("HWPC__DEBUG__END_YEAR"))
else:
    _debug_start_year = 1850
    _debug_end_year = 2050

use_s3_raw = os.getenv("HWPC__PURE_S3")
USE_S3 = True

CDN_PATH = os.getenv("HWPC__CDN_URI")

if use_s3_raw.lower().find("f") >= 0 or use_s3_raw.lower().find("0") >= 0 or CDN_PATH is not None:
    USE_S3 = False


int_16_str = "int16"
int_32_str = "int32"
int_64_str = "int64"

float_32_str = "float32"
float_64_str = "float64"


class ModelData(pickler.Pickler):
    """TODO Description

    Attributes:
        data (dict):
            describe
        ids (xr.Dataset):
            describe
        region (str):
            ?
        decay_function (str):
            describe
        input_path (str):
            describe
        output_path (dict):
            describe
        scenario_info (dict):
            describe
    """

    def __init__(self, *args, **kwargs) -> None:
        self.data = dict()
        self.ids = None
        self.region = None
        self.decay_function = None
        print("kwargs:", kwargs)
        self.run_name = kwargs["run_name"]
        self.input_path = kwargs["input_path"]
        print(self.input_path)
        self.output_path = kwargs["output_path"]

        self.scenario_info = None  # Defined in load_data

        self.load_data(path_override=self.input_path)
        self.prep_data()

        return

    def factory(run_name, input_path, output_path):
        return ModelData(run_name=run_name, input_path=input_path, output_path=output_path)

    def load_data(self, path_override=None) -> None:
        """Read data into pandas DataFrames"""
        json_file = s3_helper.S3Helper.download_file("hwpc", path_override + "/user_input.json")

        with open(json_file.name) as f:
            j = json.load(f)
            self.scenario_info = j  # NOTE!
            self.region = j["region"]["name"]
            self.decay_function = j["decay_function"]
            for k in j:
                if k == "inputs":
                    for l in j[k]:
                        if (j[k][l]) == "Default Data":
                            if USE_S3:
                                default_csv = s3_helper.S3Helper.download_file("hwpc", "default-data/" + l)
                                with open(BytesIO(default_csv), "rb") as csv:
                                    self.data[l.replace(".csv", "")] = pd.read(csv)
                            else:
                                r = requests.get(CDN_PATH + "default-data/" + l)
                                if r.status_code != 200:
                                    raise PermissionError()
                                default_csv = r.content
                                self.data[l.replace(".csv", "")] = pd.read_csv(BytesIO(default_csv))
                        else:
                            if USE_S3:
                                user_csv = s3_helper.S3Helper.download_file("hwpc", path_override + "/" + l)
                                with open(BytesIO(user_csv), "rb") as csv:
                                    self.data[l.replace(".csv", "")] = pd.read_csv(csv)
                            else:
                                r = requests.get(CDN_PATH + path_override + "/" + l)
                                if r.status_code != 200:
                                    raise PermissionError()
                                user_csv = r.content
                                self.data[l.replace(".csv", "")] = pd.read_csv(BytesIO(user_csv))
        return

    def prep_data(self) -> None:
        """TODO This function should do any functions needed to prepare data for use.
        Examples could be sorting years, checking for matching yearly data, ratios summing
        to zero, etc.
        TODO lots of repeated code here... could probably improve this
        """
        df = self.data[nm.Tables.harvest]
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype(int_16_str)
        df[nm.Fields.ccf] = df[nm.Fields.ccf].astype(float_64_str)
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
        dx = dx.where(dx.coords[nm.Fields.harvest_year] >= _debug_start_year, drop=True)
        dx = dx.where(dx.coords[nm.Fields.harvest_year] <= _debug_end_year, drop=True)

        self.data[nm.Tables.harvest] = dx

        # TODO This does not work post S3 update
        # if self.data[nm.Tables.harvest_data_type].columns.values[0] == "mbf":
        #     self._get_mbf_conversion()

        df = self.data[nm.Tables.timber_products_ratios]
        # Just in case the year was read as a string, parse to numeric
        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year], downcast="integer")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype(int_16_str)
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype(int_16_str)
        if nm.Fields.ratio in df.columns:
            df = df.rename(columns={nm.Fields.ratio: nm.Fields.timber_product_ratio})
        df[nm.Fields.timber_product_ratio] = df[nm.Fields.timber_product_ratio].astype(float_64_str)
        tr = df
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.timber_product_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        self.data[nm.Tables.timber_products_ratios] = dx

        df = self.data[nm.Tables.timber_products]
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype(int_16_str)
        df = df.set_index([nm.Fields.timber_product_id])
        dx = df.to_xarray()
        self.data[nm.Tables.timber_products] = dx

        # Parse the region and attempt to pull in default data
        region_match = self.get_region_id(self.region)

        df = self.data[nm.Tables.primary_product_ratios]

        # TODO after data revisions, check that region matching still works
        if region_match:
            self.data[nm.Tables.primary_product_ratios] = df[df[nm.Fields.region_id] == region_match]
            df = df[df[nm.Fields.region_id] == region_match]
        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year])
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype(int_16_str)
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype(int_16_str)
        if nm.Fields.ratio in df.columns:
            df = df.rename(columns={nm.Fields.ratio: nm.Fields.primary_product_ratio})
        df[nm.Fields.primary_product_ratio] = df[nm.Fields.primary_product_ratio].astype(float_64_str)
        pr = df
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.primary_product_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        self.data[nm.Tables.primary_product_ratios] = dx

        df = self.data[nm.Tables.primary_products]
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype(int_16_str)
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype(int_16_str)
        df[nm.Fields.conversion_factor] = df[nm.Fields.conversion_factor].astype(float_64_str)
        df[nm.Fields.ratio_group] = df[nm.Fields.ratio_group].astype(int_16_str)
        df[nm.Fields.fuel] = df[nm.Fields.fuel].astype(int_16_str)
        pp = df
        df = df.set_index([nm.Fields.primary_product_id])
        dx = df.to_xarray()
        self.data[nm.Tables.primary_products] = dx

        df = self.data[nm.Tables.end_use_product_ratios]
        df[nm.Fields.end_use_id] = df[nm.Fields.end_use_id].astype(int_16_str)
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype(int_16_str)
        df[nm.Fields.end_use_ratio] = df[nm.Fields.end_use_ratio].astype(float_64_str)
        er = df
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.end_use_id])

        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        self.data[nm.Tables.end_use_product_ratios] = dx

        # Make the big lookup table which multiplies out the harvest-to-product ratios and
        # adds the primary product MTC conversion
        ids = self.data[nm.Tables.ids]
        ppcf = pp[[nm.Fields.primary_product_id, nm.Fields.conversion_factor]]
        final = (
            ids.merge(tr, on=nm.Fields.timber_product_id)
            .merge(pr, on=[nm.Fields.harvest_year, nm.Fields.primary_product_id])
            .merge(ppcf, on=[nm.Fields.primary_product_id])
            .merge(er, on=[nm.Fields.harvest_year, nm.Fields.end_use_id])
        )
        final[nm.Fields.primary_product_ratio_direct] = final[nm.Fields.timber_product_ratio] * final[nm.Fields.primary_product_ratio]
        final[nm.Fields.end_use_ratio_direct] = (
            final[nm.Fields.timber_product_ratio]
            * final[nm.Fields.primary_product_ratio]
            * final[nm.Fields.end_use_ratio]
            * final[nm.Fields.conversion_factor]
        )
        final[nm.Fields.timber_product_id] = final[nm.Fields.timber_product_id].astype(int_16_str)
        final[nm.Fields.primary_product_id] = final[nm.Fields.primary_product_id].astype(int_16_str)
        final[nm.Fields.end_use_id] = final[nm.Fields.end_use_id].astype(int_16_str)
        final = final.set_index([nm.Fields.harvest_year, nm.Fields.end_use_id])
        final_x = final.to_xarray()

        self.ids = final_x

        df = self.data[nm.Tables.end_use_products]
        df[nm.Fields.end_use_id] = df[nm.Fields.end_use_id].astype(int_16_str)
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype(int_16_str)
        df[nm.Fields.end_use_halflife] = df[nm.Fields.end_use_halflife].astype(float_64_str)
        df[nm.Fields.ratio_group] = df[nm.Fields.ratio_group].astype(int_16_str)
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype(int_16_str)
        df[nm.Fields.fuel] = df[nm.Fields.fuel].astype(int_16_str)
        df = df.set_index([nm.Fields.end_use_id])
        dx = df.to_xarray()
        self.data[nm.Tables.end_use_products] = dx

        df = self.data[nm.Tables.discard_destination_ratios]
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype(int_16_str)
        df[nm.Fields.discard_destination_id] = df[nm.Fields.discard_destination_id].astype(int_16_str)
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype(int_16_str)
        df[nm.Fields.discard_destination_ratio] = df[nm.Fields.discard_destination_ratio].astype(float_64_str)
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.discard_type_id, nm.Fields.discard_destination_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        self.data[nm.Tables.discard_destination_ratios] = dx

        df = self.data[nm.Tables.discard_destinations]
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype(int_16_str)
        df[nm.Fields.discard_destination_id] = df[nm.Fields.discard_destination_id].astype(int_16_str)
        df[nm.Fields.fixed_ratio] = df[nm.Fields.fixed_ratio].astype(float_64_str)
        df[nm.Fields.halflife] = df[nm.Fields.halflife].astype(float_64_str)
        df = df.set_index([nm.Fields.discard_type_id, nm.Fields.discard_destination_id])
        dx = df.to_xarray()
        self.data[nm.Tables.discard_destinations] = dx

        return

    def get_region_id(self, region: str) -> int:
        """Get the region ID from a string value.
        TODO add checking for valid string

        Args:
            region (str): The region to lookup

        Returns:
            int: A numeric ID for the region
        """
        regions = self.data[nm.Tables.regions]
        if region in regions[nm.Fields.region_name].unique():
            match_region = regions.loc[regions[nm.Fields.region_name] == region]["Region" + nm.Fields.id].iloc[0]
        else:
            match_region = None
        return match_region

    def _get_mbf_conversion(self):
        """Expands mbf_to_ccf_conversion.csv from small number of years to ratio per year"""
        # TODO this needs to be updated to xarray
        year_group = {}
        self.data[nm.Tables.mbf_conversion] = pd.read_csv("data/mbf_to_ccf_conversion.csv")

        for i in range(self.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].size):
            year_set = []

            if i < self.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].size - 1:
                for j in range(
                    self.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].values[i],
                    self.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].values[i + 1],
                ):
                    year_set.append(j)
            else:
                for j in range(
                    self.data[nm.Tables.mbf_conversion][nm.Fields.harvest_year].values[i],
                    self.data[nm.Tables.harvest][nm.Fields.harvest_year].max(),
                ):
                    year_set.append(j)

            year_set = tuple(year_set)
            year_group[i] = year_set, self.data[nm.Tables.mbf_conversion][nm.Fields.conversion_factor].values[i]

        temp = pd.DataFrame.from_dict(
            year_group,
            orient="index",
            columns=[nm.Fields.harvest_year, nm.Fields.conversion_factor],
        )
        temp = temp.explode(nm.Fields.harvest_year).reset_index(drop=True)

        self.data[nm.Tables.harvest] = self.data[nm.Tables.harvest].merge(temp, on=nm.Fields.harvest_year, how="inner")
        self.data[nm.Tables.harvest][nm.Fields.ccf] = (
            self.data[nm.Tables.harvest][nm.Fields.mbf] * self.data[nm.Tables.harvest][nm.Fields.conversion_factor]
        )

        return
