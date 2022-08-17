from datetime import timedelta
import math
import numpy as np
import pandas as pd
import timeit
import dask.bag as db
import dask.dataframe as dd
import dask.delayed
from dask.distributed import Client, LocalCluster, get_client, Lock
import xarray as xr

from hwpc import model_data_xr as model_data

# from hwpc import results
from hwpc.names import Names as nm

from utils import singleton


class Meta(singleton.Singleton):
    def __new__(cls, *args, **kwargs):
        if Meta._instance is None:
            super().__new__(cls, args, kwargs)

            # Meta.cluster = LocalCluster(n_workers=8, processes=False)
            # Meta.client = Client(Meta.cluster)

            # Meta.lock = Lock()

            Meta.model_collection = dict()
            Meta.model_list = list()

        return cls._instance

    @classmethod
    def reset(cls):
        del Meta._instance
        Meta.client.close()
        Meta.cluster.close()

        return Meta()

    @staticmethod
    def run_simulation():
        md = model_data.ModelData()
        harvest = md.data[nm.Tables.harvest]

        ModelFactory(harvest_init=harvest)

        return

    @staticmethod
    def run_simulation_dask():
        md = model_data.ModelData()
        harvest = md.data[nm.Tables.harvest]

        ModelFactory(harvest_init=harvest)

        run_k = dict()

        all_results = dict()

        last_k = None
        while True:
            ks = list(Meta.model_collection)
            if last_k == ks:
                all_results = results
                break
            for k in ks:
                if last_k is None or k not in last_k:
                    run_k[k] = Meta.model_collection[k]
                    # Meta.client.submit(run_k[k])
            results = Meta.client.gather(run_k.values())
            last_k = ks

        # bag = db.from_sequence(run_k)

        return all_results


class ModelFactory(object):
    def __init__(self, harvest_init=None, lineage=None, recycled=None):

        years = harvest_init[nm.Fields.harvest_year]  # .unique().astype(int)
        first_year = years.min().item()
        last_year = years.max().item()

        if recycled is not None:
            years = recycled[nm.Fields.harvest_year]  # .unique().astype(int)
            first_year = years.min().item()

        # Create the dataframes needed to run each harvest year or recycle year "independently"
        for year in years:
            y = year.item()
            # An extra year is now added during prep_data, so we don't simulate on it
            if y == last_year:
                continue

            if lineage is None:
                k = (y,)
            else:
                lineage = list(lineage)
                k = lineage + [y]
                k = tuple(k)

            if recycled is not None:
                year_recycled = recycled.copy(deep=True)
                year_recycled = year_recycled.where(year_recycled.coords[nm.Fields.harvest_year] >= year, drop=True)
                year_recycled[nm.Fields.products_in_use] = xr.where(
                    year_recycled[nm.Fields.harvest_year] == year, year_recycled[nm.Fields.products_in_use], 0
                )

                m = Model(harvest=harvest_init, recycled=year_recycled, lineage=k)
            else:
                # Get the harvest record for this year
                harvest = harvest_init.where(harvest_init.coords[nm.Fields.harvest_year] >= y, drop=True)
                harvest = harvest.where(harvest.coords[nm.Fields.harvest_year] == y, 0)

                m = Model(harvest=harvest, lineage=k)

            Meta.model_collection[k] = m
            Meta.model_list.append(m)

            # client = get_client()
            # client.submit(m.run)
            # client.log_event("New Sim", "Lineage: " + str(k))
        return


class Model(object):
    def __init__(self, harvest=None, recycled=None, lineage=None) -> None:
        """Constructor for the Model object

        Args:
            harvest_init:
                For passing a set of harvest data to the model. Used for
                feeding recycled products back into the model as a new
                "harvest" to model

        """

        self.md = model_data.ModelData()  # This is a singleton, so this is not expensive

        self.harvests = harvest
        self.recycled = recycled
        # self.results = results.Results(recycled=recycled_link is not None)
        self.lineage = lineage

        # the amount of product that is not lost
        self.end_use_loss_factor = float(self.md.data[nm.Tables.loss_factor].columns.values[0])

        # User inputs delivered to results
        # self.results.harvest_data = self.harvests
        # self.results.timber_products_data = self.md.data[
        #     "pre_" + nm.Tables.timber_products_data
        # ]
        # self.results.primary_products_data = self.md.data[
        #     nm.Tables.primary_products_data
        # ]

    # @dask.delayed
    def run(self):

        if self.recycled is None:
            self.working_table = self.harvests.merge(self.md.ids, join="left", fill_value=0)
            # self.working_table = self.harvests
            # self.working_table = self.calculate_primary_product_mcg(self.working_table)
            self.working_table = self.calculate_end_use_products(self.working_table)
            self.working_table = self.calculate_products_in_use(self.working_table)
        else:
            self.working_table = self.recycled

        self.working_table = self.working_table.assign_attrs({"lineage": self.lineage})

        # self.working_table = dd.from_pandas(
        #     self.working_table, npartitions=self.recycled.shape[0] // 3
        # )
        self.working_table = self.calculate_discarded_dispositions(self.working_table)
        self.working_table = self.calculate_dispositions(self.working_table)
        # self.calculate_fuel_burned()
        # self.calculate_discarded_burned()
        # self.summarize()
        # self.convert_c02_e()
        # self.final_table()

        # self.results.save_output()

        return self.working_table

    # @dask.delayed
    def calculate_primary_product_mcg(self, working_table):
        """Calculate the amounts of primary products (MgC) harvested in each year."""
        # TODO this needs reworked using the new ids system. The new system bypasses the intermedate
        # harvest conversion (timber->primary) but we still need that info for results.

        # Calculate timber products (CCF) by multiplying the harvest-to-timber ratio for each
        # timber product by the amount harvested that year.

        # timber_products = working_table.merge(self.md.data[nm.Tables.timber_products_ratios], join="left", fill_value=0.0)
        timber_products = working_table.merge(self.md.data[nm.Tables.timber_products], join="left", compat="override")
        timber_products[nm.Fields.timber_product_results] = timber_products[nm.Fields.timber_product_ratio] * timber_products[nm.Fields.ccf]

        # self.results.timber_products = timber_products
        # self.results.harvests = self.harvests

        # Calculate primary products (CCF) by multiplying the timber-to-primary ratio for each
        # primary product by the amount of the corresponding timber product. Then convert to MgC
        # by multiplying by the CCF-to-MgC ratio for that primary product.
        primary_products = self.md.data[nm.Tables.primary_products]

        primary_products = working_table.merge(primary_products, join="left", compat="override")
        primary_products[nm.Fields.primary_product_results] = (
            primary_products[nm.Fields.primary_product_ratio_direct] * primary_products[nm.Fields.ccf]
        )

        primary_products[nm.Fields.primary_product_results] = (
            primary_products[nm.Fields.primary_product_results] * primary_products[nm.Fields.conversion_factor]
        )

        # Get the sum total of primary products now that it's converted to MgC
        tmbr = (
            primary_products[[nm.Fields.harvest_year, nm.Fields.ccf, nm.Fields.primary_product_results]]
            .groupby(nm.Fields.harvest_year)
            .sum(dim=nm.Fields.primary_product_id)
        )
        tmbr = tmbr.merge(self.harvests)

        # self.results.annual_timber_products = tmbr
        # self.results.primary_products = primary_products
        # self.results.working_table = primary_products

        return primary_products

    # @dask.delayed
    def calculate_end_use_products(self, working_table):
        """Calculate the amount of end use products harvested in each year."""

        # Multiply the primary-to-end-use ratio for each end use product by the amount of the
        # corresponding primary product.
        # end_use = working_table.merge(self.md.data[nm.Tables.end_use_product_ratios], join="left", fill_value=0.0)
        # end_use[nm.Fields.end_use_results] = end_use[nm.Fields.end_use_ratio] * end_use[nm.Fields.primary_product_results]

        end_use = working_table
        end_use[nm.Fields.end_use_results] = working_table[nm.Fields.ccf] * working_table[nm.Fields.end_use_ratio_direct]

        # self.results.end_use_products = end_use
        # self.results.working_table = end_use

        return end_use

    @staticmethod
    def halflife_func(df):
        md = model_data.ModelData()
        hl = df[nm.Fields.end_use_halflife].item()
        if hl == 0:
            df[nm.Fields.products_in_use] = df[nm.Fields.end_use_results]
        else:
            v = df[nm.Fields.end_use_sum][0].item()
            decayed = [v * math.exp(-math.log(2) * x / hl) for x in range(len(df.coords[nm.Fields.harvest_year]))]
            dd = xr.DataArray(decayed, dims=nm.Fields.harvest_year, coords={nm.Fields.harvest_year: df.coords[nm.Fields.harvest_year]}).astype(
                "float32"
            )
            df[nm.Fields.products_in_use] = dd
        return df

    @staticmethod
    def chi_func(df):

        return

    # @dask.delayed
    def calculate_products_in_use(self, working_table):
        """Calculate the amount of end use products from each vintage year that are still in use
        during each inventory year.
        """
        # Make sure the rows are ascending to do the half life. Don't do this inplace
        # end_use = end_use.sort_values(by=nm.Fields.harvest_year)
        end_use = working_table.merge(
            self.md.data[nm.Tables.end_use_products],
            join="left",
            compat="override",
            fill_value=0,
        )

        loss = 1 - float(self.md.data[nm.Tables.loss_factor].columns.values[0])
        end_use[nm.Fields.end_use_sum] = xr.where(
            end_use[nm.Fields.discard_type_id] == 0, end_use[nm.Fields.end_use_results], end_use[nm.Fields.end_use_results] * loss
        )
        products_in_use = end_use.groupby(nm.Fields.end_use_id).map(Model.halflife_func)

        # self.results.products_in_use = products_in_use
        # self.results.working_table = products_in_use

        return products_in_use

    # @dask.delayed
    def calculate_discarded_dispositions(self, working_table):
        """Calculate the amount discarded during each inventory year and divide it up between the
        different dispositions (landfills, dumps, etc).
        """

        # Calculate the amount of each end use from year y that was discarded in year i
        # by subtracting the products in use from the amount of harvested product and
        # then subtracting the amount discarded in previous years.
        products_in_use = working_table
        products_in_use[nm.Fields.discarded_products_results] = products_in_use[nm.Fields.end_use_sum] - products_in_use[nm.Fields.products_in_use]

        # Tease out the NEW discarded amounts for this year to dispose of them in the correct pools
        adjust = products_in_use[nm.Fields.discarded_products_results].shift({nm.Fields.harvest_year: 1}, fill_value=0.0)
        products_in_use[nm.Fields.discarded_in_year] = products_in_use[nm.Fields.discarded_products_results] - adjust

        # Zero out the stuff that was fuel.
        # TODO need to rigorously test this that it's doing what we think
        products_in_use[nm.Fields.discarded_products_results] = products_in_use[nm.Fields.discarded_products_results].where(
            products_in_use.data_vars[nm.Fields.fuel] == 1, 0
        )

        # Multiply the amount discarded this year by the disposition ratios to get the
        # amount that goes into landfills, dumps, etc, and then add these to the
        # discarded disposition totals for stuff discarded in year i.
        paper_in_use = products_in_use.where(products_in_use[nm.Fields.discard_type_id] == 0, drop=True)  # .drop_vars(nm.Fields.discard_type_id)
        wood_in_use = products_in_use.where(products_in_use[nm.Fields.discard_type_id] == 1, drop=True)  # .drop_vars(nm.Fields.discard_type_id)

        discard_ratios = self.md.data[nm.Tables.discard_destination_ratios]
        paper_discard_ratios = (
            discard_ratios.where(discard_ratios[nm.Fields.discard_type_id] == 0, drop=True).squeeze().drop_vars(nm.Fields.discard_type_id)
        )
        wood_discard_ratios = (
            discard_ratios.where(discard_ratios[nm.Fields.discard_type_id] == 1, drop=True).squeeze().drop_vars(nm.Fields.discard_type_id)
        )

        paper_in_use[nm.Fields.discard_dispositions] = (
            paper_in_use[nm.Fields.discarded_in_year] * paper_discard_ratios[nm.Fields.discard_destination_ratio]
        )
        wood_in_use[nm.Fields.discard_dispositions] = (
            wood_in_use[nm.Fields.discarded_in_year] * wood_discard_ratios[nm.Fields.discard_destination_ratio]
        )

        products_in_use = xr.merge([paper_in_use, wood_in_use])

        # self.results.discarded_products = products_in_use
        # self.results.working_table = products_in_use

        return products_in_use

    # @dask.delayed
    def calculate_dispositions(self, working_table):
        """Calculate the amounts of discarded products that have been emitted, are still remaining,
        etc., for each inventory year.
        """

        # Calculate the amount in landfills that was discarded during this inventory year
        # that is subject to decay by multiplying the amount in the landfill by the
        # landfill-fixed-ratio. This will be used in later iterations of the i loop.
        destinations = self.md.data[nm.Tables.discard_destinations]
        # TODO make the ID lookup dynamic. For now we just need this done so hard code it
        # landfill_id = destinations.where(destinations == nm.Fields.landfills, drop=True)[nm.Fields.discard_destination_id].item()
        # recycled_id = destinations.where(destinations == nm.Fields.recycled, drop=True)[nm.Fields.discard_destination_id].item()
        landfill_id = 3
        recycled_id = 1

        # Calculate the amount in landfills that was discarded during this inventory year
        # that is subject to decay by multiplying the amount in the landfill by the
        # landfill-fixed-ratio.
        paper_dispositions = working_table.where(working_table[nm.Fields.discard_type_id] == 0, drop=True)
        wood_dispositions = working_table.where(working_table[nm.Fields.discard_type_id] == 1, drop=True)

        paper_destinations = (
            destinations.where(destinations[nm.Fields.discard_type_id] == 0, drop=True).squeeze().drop_vars(nm.Fields.discard_type_id)
        )
        wood_destinations = destinations.where(destinations[nm.Fields.discard_type_id] == 1, drop=True).squeeze().drop_vars(nm.Fields.discard_type_id)

        paper_dispositions[nm.Fields.can_decay] = paper_dispositions[nm.Fields.discard_dispositions] * (1 - paper_destinations[nm.Fields.fixed_ratio])
        paper_dispositions[nm.Fields.halflife] = paper_destinations[nm.Fields.halflife]
        wood_dispositions[nm.Fields.can_decay] = wood_dispositions[nm.Fields.discard_dispositions] * (1 - wood_destinations[nm.Fields.fixed_ratio])
        wood_dispositions[nm.Fields.halflife] = wood_destinations[nm.Fields.halflife]

        dispositions = xr.merge([paper_dispositions, wood_dispositions])

        # For the new recycling, remove products assigned to be recycled and
        # begin a new simulation using the recycled products as "harvest" amounts
        # TODO the below line doesn't work, it resets coords in a bad way. Hard coding selection.
        # recycled = dispositions.where(dispositions.coords[nm.Fields.discard_destination_id] == recycled_id, drop=True)
        recycled = dispositions.loc[dict(DiscardDestinationID=recycled_id)]

        # Set the recycled material to be "in use" in the next year
        recycled[nm.Fields.products_in_use] = recycled[nm.Fields.can_decay]
        recycled[nm.Fields.harvest_year] = recycled[nm.Fields.harvest_year] + 1

        # keep_key = [
        #     nm.Fields.harvest_year,
        #     nm.Fields.ccf,
        #     nm.Fields.timber_product_id,
        #     nm.Fields.timber_product_ratio,
        #     nm.Fields.timber_product_results,
        #     nm.Fields.primary_product_id,
        #     nm.Fields.primary_product_ratio,
        #     nm.Fields.primary_product_results,
        #     nm.Fields.conversion_factor,
        #     nm.Fields.end_use_id,
        #     nm.Fields.end_use_ratio,
        #     nm.Fields.end_use_results,
        #     nm.Fields.discard_description,
        #     nm.Fields.end_use_halflife,
        #     nm.Fields.ratio_group,
        #     nm.Fields.discard_type_id,
        #     nm.Fields.fuel,
        #     nm.Fields.end_use_sum,
        #     nm.Fields.products_in_use,
        # ]

        drop_key = [nm.Fields.discarded_products_results, nm.Fields.discarded_in_year, nm.Fields.discard_dispositions, nm.Fields.can_decay]

        recycled = recycled.drop_vars(drop_key)

        zero_key = [
            nm.Fields.ccf,
            nm.Fields.end_use_results,
            nm.Fields.end_use_sum,
            nm.Fields.products_in_use,
        ]

        # Zero out harvest info because recycled material isn't harvested
        recycled = xr.zeros_like(recycled[zero_key]).drop_vars(nm.Fields.discard_destination_id)

        nonrecycled = dispositions.where(dispositions.coords[nm.Fields.discard_destination_id] != recycled_id, drop=True)

        # with Meta.lock:
        #     print("==================================")
        #     print("Lineage:", self.lineage)
        #     print("Recycled Size:", recycled.shape)
        #     print("Nonrecycled Size:", nonrecycled.shape)
        #     print("==================================")
        print("Lineage:", self.lineage)

        ModelFactory(harvest_init=self.harvests, recycled=recycled, lineage=self.lineage)

        # Calculate the amounts that were discarded in year y that could decay but
        # are still remaining in year i, by plugging the amount subject to decay into
        # the decay formula that uses half lives.

        def halflife_func(df):
            hl = df[nm.Fields.halflife].item()

            if hl == 0:
                df[nm.Fields.discard_remaining] = 0
            else:
                v = df[nm.Fields.can_decay][0].item()
                decayed = [v * math.exp(-math.log(2) * x / hl) for x in range(len(df.coords[nm.Fields.harvest_year]))]
                dd = xr.DataArray(decayed, dims=nm.Fields.harvest_year, coords={nm.Fields.harvest_year: df.coords[nm.Fields.harvest_year]}).astype(
                    "float32"
                )
                df[nm.Fields.discard_remaining] = dd
            return df

        df_key = [
            nm.Fields.end_use_id,
            nm.Fields.discard_destination_id,
        ]

        s = timeit.default_timer()
        nonrecycled = nonrecycled.stack(k=df_key)
        dispositions = nonrecycled.groupby("k").apply(halflife_func)
        # print("DISPOSITIONS APPLY", timeit.default_timer() - s)

        dispositions[nm.Fields.could_decay] = dispositions.groupby("k")[nm.Fields.can_decay].cumsum()

        # Calculate emissions from stuff discarded in year y by subracting the amount
        # remaining from the total amount that could decay.
        dispositions[nm.Fields.emitted] = dispositions[nm.Fields.could_decay] - dispositions[nm.Fields.discard_remaining]
        dispositions[nm.Fields.present] = dispositions[nm.Fields.discard_remaining]

        # Landfills are a bit different. Not all of it is subject to decay, so get the fixed amount and add it to present through time
        df_filter = (dispositions[nm.Fields.discard_destination_id] == landfill_id) & (dispositions[nm.Fields.discard_type_id] == self.md.paper_val)
        dispositions.loc[df_filter, nm.Fields.present] = dispositions.loc[df_filter, nm.Fields.present] + (
            dispositions.loc[df_filter, nm.Fields.discard_dispositions] * discard_types[nm.Fields.paper][nm.Fields.landfill_fixed_ratio]
        )

        df_filter = (dispositions[nm.Fields.discard_destination_id] == landfill_id) & (dispositions[nm.Fields.discard_type_id] == self.md.wood_val)
        dispositions.loc[df_filter, nm.Fields.present] = dispositions.loc[df_filter, nm.Fields.present] + (
            dispositions.loc[df_filter, nm.Fields.discard_dispositions] * discard_types[nm.Fields.wood][nm.Fields.landfill_fixed_ratio]
        )

        # self.results.dispositions = dispositions
        # self.results.working_table = dispositions

        return dispositions

    # # @dask.delayed
    # def calculate_fuel_burned(self):
    #     """Calculate the amount of fuel burned during each vintage year."""
    #     dispositions = self.results.working_table

    #     # Loop through all of the primary products that are fuel and add the amounts of that
    #     # product to the total for this year.
    #     df_keys = [
    #         nm.Fields.harvest_year,
    #         nm.Fields.primary_product_id,
    #         nm.Fields.emitted,
    #     ]
    #     fuel_captured = dispositions.loc[
    #         dispositions[nm.Fields.fuel] == 1, df_keys
    #     ].drop_duplicates()

    #     self.results.fuelwood = fuel_captured

    #     return

    # # @dask.delayed
    # def calculate_discarded_burned(self):
    #     """Calculate the amount of discarded products that were burned."""
    #     # For each year, sum up the amount of discarded paper and wood that are burned, and then
    #     # multiply that by the burned-with-energy-capture ratio for that year.

    #     dispositions = self.results.working_table
    #     dispositions_not_fuel = dispositions[dispositions[nm.Fields.fuel] == 0]

    #     discard_destinations = self.md.data[nm.Tables.discard_destinations]
    #     burned = discard_destinations[
    #         discard_destinations[nm.Fields.discard_description] == nm.Fields.burned
    #     ][nm.Fields.discard_destination_id].iloc[0]

    #     burned_wo_energy_capture = dispositions_not_fuel[
    #         dispositions_not_fuel[nm.Fields.discard_destination_id] == burned
    #     ]
    #     self.results.burned_wo_energy_capture = burned_wo_energy_capture
    #     burned_energy_capture = pd.DataFrame(self.md.data[nm.Tables.energy_capture])
    #     burned_w_energy_capture = burned_wo_energy_capture.merge(
    #         burned_energy_capture, on=nm.Fields.harvest_year, how="inner"
    #     )
    #     burned_w_energy_capture[nm.Fields.burned_with_energy_capture] = (
    #         burned_w_energy_capture[nm.Fields.emitted]
    #         * burned_w_energy_capture[nm.Fields.percent_burned]
    #     )
    #     self.results.burned_w_energy_capture = burned_w_energy_capture

    #     return

    # # @dask.delayed
    # def summarize(self):
    #     P = nm.Fields.ppresent
    #     E = nm.Fields.eemitted

    #     results = self.results.working_table

    #     df_keys = [nm.Fields.harvest_year, nm.Fields.products_in_use]
    #     products_in_use = (
    #         results.loc[:, df_keys]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.products_in_use: np.sum})
    #     )
    #     self.results.products_in_use = products_in_use

    #     # Get discard destination IDs for sorting through results
    #     discard_destinations = self.md.data[nm.Tables.discard_destinations]

    #     # For burned and composted, we can directly get the emissions from the results table
    #     df_keys = [nm.Fields.harvest_year, nm.Fields.emitted]

    #     # Get the burned records from results. We want to save the emitted amount, which for burned is all accounted for carbon
    #     burned_id = discard_destinations[
    #         discard_destinations[nm.Fields.discard_description] == nm.Fields.burned
    #     ][nm.Fields.discard_destination_id].iloc[0]
    #     burned = (
    #         results.loc[results[nm.Fields.discard_destination_id] == burned_id, df_keys]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.emitted: np.sum})
    #     )
    #     burned = burned.rename(columns={nm.Fields.emitted: E(nm.Fields.burned)})
    #     self.results.burned = burned

    #     # Get the aggregation of burned emissions that are multiplied by the energy capture ratio of every year, should be 0
    #     burned_w_capture = self.results.burned_w_energy_capture
    #     burned_w_capture = burned_w_capture.groupby(by=nm.Fields.harvest_year).agg(
    #         {nm.Fields.burned_with_energy_capture: np.sum}
    #     )
    #     self.results.burned_w_energy_capture = burned_w_capture

    #     burned_wo_capture = self.results.burned_wo_energy_capture
    #     burned_wo_capture = burned_wo_capture.groupby(by=nm.Fields.harvest_year).agg(
    #         {nm.Fields.emitted: np.sum}
    #     )
    #     self.results.burned_wo_energy_capture = burned_wo_capture

    #     # Now get composted. Same process as burned
    #     composted_id = discard_destinations[
    #         discard_destinations[nm.Fields.discard_description] == nm.Fields.composted
    #     ][nm.Fields.discard_destination_id].iloc[0]
    #     composted = (
    #         results.loc[
    #             results[nm.Fields.discard_destination_id] == composted_id, df_keys
    #         ]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.emitted: np.sum})
    #     )
    #     composted = composted.rename(
    #         columns={nm.Fields.emitted: E(nm.Fields.composted)}
    #     )
    #     self.results.composted = composted

    #     # For the SWDS emissions, we want to get the amount present before getting the amount emitted
    #     df_keys = [nm.Fields.harvest_year, nm.Fields.present]

    #     # Start with recovered AKA recycled present. This might mean "in use", but recycled rather than directly used from harvest
    #     recycled_id = discard_destinations[
    #         discard_destinations[nm.Fields.discard_description] == nm.Fields.recycled
    #     ][nm.Fields.discard_destination_id].iloc[0]
    #     recovered_in_use = (
    #         results.loc[
    #             results[nm.Fields.discard_destination_id] == recycled_id, df_keys
    #         ]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.present: np.sum})
    #     )
    #     recovered_in_use = recovered_in_use.rename(
    #         columns={nm.Fields.present: P(nm.Fields.recycled)}
    #     )
    #     self.results.recovered_in_use = recovered_in_use

    #     # Get landfill present
    #     landfill_id = discard_destinations[
    #         discard_destinations[nm.Fields.discard_description] == nm.Fields.landfills
    #     ][nm.Fields.discard_destination_id].iloc[0]
    #     in_landfills = (
    #         results.loc[
    #             results[nm.Fields.discard_destination_id] == landfill_id, df_keys
    #         ]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.present: np.sum})
    #     )
    #     in_landfills = in_landfills.rename(
    #         columns={nm.Fields.present: P(nm.Fields.landfills)}
    #     )
    #     self.results.in_landfills = in_landfills

    #     # Finally get dump amount present
    #     dump_id = discard_destinations[
    #         discard_destinations[nm.Fields.discard_description] == nm.Fields.dumps
    #     ][nm.Fields.discard_destination_id].iloc[0]
    #     in_dumps = (
    #         results.loc[results[nm.Fields.discard_destination_id] == dump_id, df_keys]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.present: np.sum})
    #     )
    #     in_dumps = in_dumps.rename(columns={nm.Fields.present: P(nm.Fields.dumps)})
    #     self.results.in_dumps = in_dumps

    #     # TODO not so suspicious after all
    #     fuelwood = self.results.fuelwood
    #     fuelwood = fuelwood.groupby(by=nm.Fields.harvest_year).agg(
    #         {nm.Fields.emitted: np.sum}
    #     )
    #     fuelwood = fuelwood.rename(columns={nm.Fields.emitted: E(nm.Fields.fuel)})
    #     self.results.fuelwood = fuelwood

    #     # Collect all the emissions to be converted to CO2e. HISTORICALLY this was only for emissions, but not everything needs to be in CO2e...
    #     df_keys = [nm.Fields.harvest_year, nm.Fields.emitted]
    #     landfills_emitted = (
    #         results.loc[
    #             results[nm.Fields.discard_destination_id] == landfill_id, df_keys
    #         ]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.emitted: np.sum})
    #     )
    #     landfills_emitted = landfills_emitted.rename(
    #         columns={nm.Fields.emitted: E(nm.Fields.landfills)}
    #     )
    #     dumps_emitted = (
    #         results.loc[results[nm.Fields.discard_destination_id] == dump_id, df_keys]
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.emitted: np.sum})
    #     )
    #     dumps_emitted = dumps_emitted.rename(
    #         columns={nm.Fields.emitted: E(nm.Fields.dumps)}
    #     )
    #     recycled_emitted = (
    #         results.loc[
    #             results[nm.Fields.discard_destination_id] == recycled_id, df_keys
    #         ]
    #         .drop_duplicates()
    #         .groupby(by=nm.Fields.harvest_year)
    #         .agg({nm.Fields.emitted: np.sum})
    #     )
    #     recycled_emitted = recycled_emitted.rename(
    #         columns={nm.Fields.emitted: E(nm.Fields.recycled)}
    #     )
    #     burned_emitted = burned
    #     compost_emitted = composted

    #     # self.results.emissions = {'fuelwood': fuelwood, 'landfills_emitted': landfills_emitted, 'dumps_emitted': dumps_emitted, 'recycled_emitted': recycled_emitted, 'burned_emitted': burned_emitted, 'compost_emitted': compost_emitted}

    #     # Merge up all the present dispositions
    #     all_in_use = products_in_use.merge(
    #         recovered_in_use, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()
    #     all_in_use = all_in_use.merge(
    #         in_landfills, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()
    #     all_in_use = all_in_use.merge(
    #         in_dumps, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()
    #     # SWDS is just the sum of landfills and dumps. Compost gets emitted, recycled is kinda "in use", and burned is directly emitted
    #     all_in_use[P(nm.Fields.swds)] = all_in_use[
    #         [P(nm.Fields.landfills), P(nm.Fields.dumps)]
    #     ].sum(axis=1)
    #     self.results.all_in_use = all_in_use

    #     # Merge up all the emissions
    #     all_emitted = landfills_emitted.merge(
    #         dumps_emitted, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()
    #     all_emitted = all_emitted.merge(
    #         recycled_emitted, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()
    #     all_emitted = all_emitted.merge(
    #         burned_emitted, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()
    #     all_emitted = all_emitted.merge(
    #         compost_emitted, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()
    #     all_emitted[nm.Fields.emitted_all] = all_emitted.sum(axis=1)
    #     self.results.all_emitted = all_emitted

    #     self.results.total_all_dispositions = all_in_use.merge(
    #         all_emitted, how="inner", on=nm.Fields.harvest_year
    #     ).drop_duplicates()

    #     self.results.working_table = results

    #     return

    # # @dask.delayed
    # def convert_c02_e(self):
    #     C = nm.Fields.c
    #     CO2 = nm.Fields.co2
    #     P = nm.Fields.ppresent
    #     E = nm.Fields.eemitted

    #     total_all_dispositions = self.results.total_all_dispositions

    #     # Pull in fuel here too... I think it needs converting just like the rest
    #     total_all_dispositions = total_all_dispositions.merge(
    #         self.results.fuelwood, on=nm.Fields.harvest_year
    #     )
    #     total_all_dispositions_co2e = total_all_dispositions.apply(
    #         self.c_to_co2e, axis=1
    #     )

    #     total_all_dispositions = total_all_dispositions.rename(lambda x: C(x), axis=1)
    #     total_all_dispositions_co2e = total_all_dispositions_co2e.rename(
    #         lambda x: CO2(x), axis=1
    #     )

    #     total_all_dispositions = total_all_dispositions.merge(
    #         total_all_dispositions_co2e, on=nm.Fields.harvest_year
    #     )

    #     # Treat the self.results.annual_timber_products before merging to only get the relevant information
    #     tmbr = self.results.annual_timber_products
    #     tmbr[C(nm.Fields.primary_product_sum)] = tmbr[
    #         nm.Fields.primary_product_results
    #     ].cumsum()
    #     tmbr[CO2(nm.Fields.primary_product_sum)] = tmbr[
    #         C(nm.Fields.primary_product_sum)
    #     ].apply(self.c_to_co2e)

    #     # Merge the harvest results into the totals table
    #     df_keys = [
    #         nm.Fields.harvest_year,
    #         C(nm.Fields.primary_product_sum),
    #         CO2(nm.Fields.primary_product_sum),
    #     ]
    #     total_all_dispositions = tmbr[df_keys].merge(
    #         total_all_dispositions, on=nm.Fields.harvest_year
    #     )

    #     df_keys = [
    #         nm.Fields.harvest_year,
    #         C(nm.Fields.primary_product_sum),
    #         CO2(nm.Fields.primary_product_sum),
    #         C(nm.Fields.products_in_use),
    #         CO2(nm.Fields.products_in_use),
    #         C(P(nm.Fields.recycled)),
    #         CO2(P(nm.Fields.recycled)),
    #         C(P(nm.Fields.swds)),
    #         CO2(P(nm.Fields.swds)),
    #         C(nm.Fields.emitted_all),
    #         CO2(nm.Fields.emitted_all),
    #     ]

    #     df_carbon = [
    #         C(nm.Fields.primary_product_sum),
    #         C(nm.Fields.products_in_use),
    #         C(P(nm.Fields.recycled)),
    #         C(P(nm.Fields.swds)),
    #         C(nm.Fields.emitted_all),
    #     ]

    #     big_table = total_all_dispositions[df_keys].drop_duplicates()
    #     big_table[nm.Fields.accounted] = big_table[df_carbon].sum(axis=1)
    #     big_table[nm.Fields.error] = (
    #         big_table[C(nm.Fields.primary_product_sum)] - big_table[nm.Fields.accounted]
    #     )

    #     big_table["pct_error"] = (
    #         big_table[nm.Fields.error] / big_table[nm.Fields.accounted]
    #     )

    #     self.results.big_table = big_table
    #     self.results.total_all_dispositions = total_all_dispositions

    #     # self.results.big_table.to_csv('x_big_table.csv')
    #     # self.results.total_all_dispositions.to_csv('x_total_all.csv')
    #     # self.results.working_table.to_csv('x_working.csv')

    #     return

    # # @dask.delayed
    # def final_table(self):

    #     final = self.results.fuelwood.merge(
    #         self.results.total_all_dispositions, on=nm.Fields.harvest_year
    #     )

    #     C = nm.Fields.c
    #     CO2 = nm.Fields.co2
    #     CHANGE = nm.Fields.change
    #     P = nm.Fields.ppresent
    #     E = nm.Fields.eemitted

    #     final[CHANGE(C(E(nm.Fields.fuel)))] = final[C(E(nm.Fields.fuel))].diff()
    #     final[CHANGE(C(nm.Fields.emitted_all))] = final[C(nm.Fields.emitted_all)].diff()
    #     final[CHANGE(C(nm.Fields.products_in_use))] = final[
    #         C(nm.Fields.products_in_use)
    #     ].diff()
    #     final[CHANGE(C(P(nm.Fields.swds)))] = final[C(P(nm.Fields.swds))].diff()

    #     final[CHANGE(CO2(E(nm.Fields.fuel)))] = final[CO2(E(nm.Fields.fuel))].diff()
    #     final[CHANGE(CO2(nm.Fields.emitted_all))] = final[
    #         CO2(nm.Fields.emitted_all)
    #     ].diff()
    #     final[CHANGE(CO2(nm.Fields.products_in_use))] = final[
    #         CO2(nm.Fields.products_in_use)
    #     ].diff()
    #     final[CHANGE(CO2(P(nm.Fields.swds)))] = final[CO2(P(nm.Fields.swds))].diff()

    #     self.results.final = final

    #     self.results.big_table.to_csv("x_big_table.csv")
    #     self.results.total_all_dispositions.to_csv("x_total_all.csv")
    #     self.results.working_table.to_csv("x_working.csv")
    #     self.results.final.to_csv("x_final.csv")

    #     return

    # def c_to_co2e(self, c: float) -> float:
    #     """Convert C to CO2e.

    #     Args:
    #         c (float): the C value to convert

    #     Returns:
    #         float: Units of CO2
    #     """
    #     return c * 44.0 / 12.0

    # def print_debug_df(self, df):
    #     """Print the head and tail of a DataFrame to console. Useful for testing

    #     Args:
    #         df (DataFrame): A DataFrame of interest to print
    #     """
    #     print(df.head(10))
    #     print(df.tail(10))

    # def memory_usage(self, df):
    #     dfm = df.memory_usage()
    #     dfm = dfm / 1024 / 1024
    #     print("\n", dfm, "\n")

    # def memory_usage_total(self, df):
    #     dfs = df.memory_usage().sum()
    #     dfs = dfs / 1024 / 1024
    #     print("{} MB used".format(dfs))
