import json
from re import X

import numpy as np
import pandas as pd
import xarray as xr
from hwpccalc.hwpc.names import Names as nm
from hwpccalc.utils import pickler, singleton, s3_helper

_debug_year = 1980


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

        return cls._instance

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        return

    @staticmethod
    def load_data(path_override=None) -> None:
        """Read data into pandas DataFrames
        TODO Right now this just looks at default data
        """
        # if path_override is None:
        #     path = "data/inputs.json"
        # print(nm.Output.output_path)
        # print(nm.Output.run_name)
        json_file = s3_helper.S3Helper.download_file("hwpc", nm.Output.input_path + "/user_input.json")

        with open(json_file.name) as f:
            j = json.load(f)
            nm.Output.scenario_info = j
            # print(j)
            for k in j:
                if k == "inputs":
                    for l in j[k]:
                        if (j[k][l]) == "Default Data":
                            default_csv = s3_helper.S3Helper.download_file("hwpc", "default-data/" + l)
                            with open(default_csv.name) as csv:
                                ModelData.data[l.replace(".csv", "")] = pd.read_csv(csv)
                        else:
                            user_csv = s3_helper.S3Helper.download_file("hwpc", nm.Output.input_path + "/" + l)
                            with open(user_csv.name) as csv:
                                ModelData.data[l.replace(".csv", "")] = pd.read_csv(csv)
                            # ModelData.data[]
                # no_csv = k.replace(".csv", "")
                # p = j[k]
                # if no_csv == nm.Tables.harvest:
                #     ks = {nm.Fields.harvest_year: "int16"}
                # ModelData.data[no_csv] = pd.read_csv(p)
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
        dx = dx.where(dx.coords[nm.Fields.harvest_year] >= _debug_year, drop=True)

        ModelData.data[nm.Tables.harvest] = dx

        # TODO This does not work post S3 update
        # if ModelData.data[nm.Tables.harvest_data_type].columns.values[0] == "mbf":
        #     ModelData._get_mbf_conversion()

        df = ModelData.data[nm.Tables.timber_products_ratios]
        # Just in case the year was read as a string, parse to numeric
        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year], downcast="integer")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype("int16")
        df[nm.Fields.timber_product_ratio] = df[nm.Fields.timber_product_ratio].astype("float32")
        tr = df
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.timber_product_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.timber_products_ratios] = dx

        df = ModelData.data[nm.Tables.timber_products]
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype("int16")
        df = df.set_index([nm.Fields.timber_product_id])
        dx = df.to_xarray()
        ModelData.data[nm.Tables.timber_products] = dx

        # Parse the region and attempt to pull in default data
        region = ModelData.data[nm.Tables.region].columns[0]
        region_match = ModelData.get_region_id(region)

        df = ModelData.data[nm.Tables.primary_product_ratios]

        # TODO after data revisions, check that region matching still works
        if region_match:
            ModelData.data[nm.Tables.primary_product_ratios] = df[df[nm.Fields.region_id] == region_match]

        df[nm.Fields.harvest_year] = pd.to_numeric(df[nm.Fields.harvest_year])
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype("int16")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.primary_product_ratio] = df[nm.Fields.primary_product_ratio].astype("float32")
        pr = df
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.primary_product_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.primary_product_ratios] = dx

        df = ModelData.data[nm.Tables.primary_products]
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype("int16")
        df[nm.Fields.timber_product_id] = df[nm.Fields.timber_product_id].astype("int16")
        df[nm.Fields.conversion_factor] = df[nm.Fields.conversion_factor].astype("float32")
        df[nm.Fields.ratio_group] = df[nm.Fields.ratio_group].astype("int16")
        df[nm.Fields.fuel] = df[nm.Fields.fuel].astype("int16")
        pp = df
        df = df.set_index([nm.Fields.primary_product_id])
        dx = df.to_xarray()
        ModelData.data[nm.Tables.primary_products] = dx

        df = ModelData.data[nm.Tables.end_use_product_ratios]
        df[nm.Fields.end_use_id] = df[nm.Fields.end_use_id].astype("int16")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.end_use_ratio] = df[nm.Fields.end_use_ratio].astype("float32")
        er = df
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.end_use_id])

        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.end_use_product_ratios] = dx

        # Make the big lookup table which multiplies out the harvest-to-product ratios and
        # adds the primary product MTC conversion
        ids = ModelData.data[nm.Tables.ids]
        ppcf = pp[[nm.Fields.primary_product_id, nm.Fields.conversion_factor]]
        final = (
            ids.merge(tr, on=nm.Fields.timber_product_id)
            .merge(pr, on=[nm.Fields.harvest_year, nm.Fields.primary_product_id])
            .merge(ppcf, on=[nm.Fields.primary_product_id])
            .merge(er, on=[nm.Fields.harvest_year, nm.Fields.end_use_id])
        )
        final[nm.Fields.primary_product_ratio_direct] = final[nm.Fields.timber_product_ratio] * final[nm.Fields.primary_product_ratio]
        final[nm.Fields.end_use_ratio_direct] = (
            final[nm.Fields.timber_product_ratio] * final[nm.Fields.primary_product_ratio] * final[nm.Fields.end_use_ratio]
        )
        final[nm.Fields.timber_product_id] = final[nm.Fields.timber_product_id].astype("int16")
        final[nm.Fields.primary_product_id] = final[nm.Fields.primary_product_id].astype("int16")
        final[nm.Fields.end_use_id] = final[nm.Fields.end_use_id].astype("int16")
        final = final.set_index([nm.Fields.harvest_year, nm.Fields.end_use_id])
        final_x = final.to_xarray()

        ModelData.ids = final_x

        df = ModelData.data[nm.Tables.end_use_products]
        df[nm.Fields.end_use_id] = df[nm.Fields.end_use_id].astype("int16")
        df[nm.Fields.primary_product_id] = df[nm.Fields.primary_product_id].astype("int16")
        df[nm.Fields.end_use_halflife] = df[nm.Fields.end_use_halflife].astype("float32")
        df[nm.Fields.ratio_group] = df[nm.Fields.ratio_group].astype("int16")
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype("int16")
        df[nm.Fields.fuel] = df[nm.Fields.fuel].astype("int16")
        df = df.set_index([nm.Fields.end_use_id])
        dx = df.to_xarray()
        ModelData.data[nm.Tables.end_use_products] = dx

        df = ModelData.data[nm.Tables.discard_destination_ratios]
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype("int16")
        df[nm.Fields.discard_destination_id] = df[nm.Fields.discard_destination_id].astype("int16")
        df[nm.Fields.harvest_year] = df[nm.Fields.harvest_year].astype("int16")
        df[nm.Fields.discard_destination_ratio] = df[nm.Fields.discard_destination_ratio].astype("float32")
        df = df.set_index([nm.Fields.harvest_year, nm.Fields.discard_type_id, nm.Fields.discard_destination_id])
        # df = df.loc[filtr, :]
        dx = df.to_xarray()
        ModelData.data[nm.Tables.discard_destination_ratios] = dx

        df = ModelData.data[nm.Tables.discard_destinations]
        df[nm.Fields.discard_type_id] = df[nm.Fields.discard_type_id].astype("int16")
        df[nm.Fields.discard_destination_id] = df[nm.Fields.discard_destination_id].astype("int16")
        df[nm.Fields.fixed_ratio] = df[nm.Fields.fixed_ratio].astype("float32")
        df[nm.Fields.halflife] = df[nm.Fields.halflife].astype("float32")
        df = df.set_index([nm.Fields.discard_type_id, nm.Fields.discard_destination_id])
        dx = df.to_xarray()
        ModelData.data[nm.Tables.discard_destinations] = dx

        return

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

        ModelData.data[nm.Tables.harvest] = ModelData.data[nm.Tables.harvest].merge(temp, on=nm.Fields.harvest_year, how="inner")
        ModelData.data[nm.Tables.harvest][nm.Fields.ccf] = (
            ModelData.data[nm.Tables.harvest][nm.Fields.mbf] * ModelData.data[nm.Tables.harvest][nm.Fields.conversion_factor]
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
