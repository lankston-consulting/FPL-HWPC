from itertools import combinations
import math
import numpy as np
import timeit
from dask.distributed import Client, LocalCluster, as_completed, get_client, Lock
# from dask_cloudprovider.aws import FargateCluster
import xarray as xr

from hwpc import model_data_xr as model_data

# from hwpc import results
from hwpc.names import Names as nm

from utils import singleton

recurse_limit = 2
first_recycle_year = 1980  # TODO make this dynamic


class Meta(singleton.Singleton):
    def __new__(cls, *args, **kwargs):
        if Meta._instance is None:
            super().__new__(cls, args, kwargs)

            Meta.cluster = LocalCluster(n_workers=8, processes=True)

            # Meta.cluster = FargateCluster()

            Meta.client = Client(Meta.cluster)

            Meta.lock = Lock("plock")

            print(Meta.client)

            # Meta.model_collection = dict()

        return cls._instance

    @staticmethod
    def model_factory(harvest_init=None, lineage=None, recycled=None):
        years = harvest_init[nm.Fields.harvest_year]
        first_year = years.min().item()
        last_year = years.max().item()

        dask_key = [first_year]

        if recycled is not None:
            years = recycled[nm.Fields.harvest_year]
            first_year = years.min().item()
            dask_key.append(first_year)

        dask_key = tuple(dask_key)
        # print("Dask Key:", dask_key)

        # Create the dataframes needed to run each harvest year or recycle year "independently"
        year_model_col = list()
        for y in range(first_year, last_year + 1):
            if lineage is None:
                k = (y,)
            else:
                lineage = list(lineage)
                k = lineage + [y]
                k = tuple(k)

            if recycled is not None:
                year_recycled = recycled.copy(deep=True)
                year_recycled = year_recycled.assign_attrs({"lineage": k})
                year_recycled = year_recycled.sel(Year=list(range(y, last_year + 1)))
                year_recycled[nm.Fields.products_in_use] = xr.where(
                    year_recycled[nm.Fields.harvest_year] == y, year_recycled[nm.Fields.products_in_use], 0
                )

                m = Model(harvest=harvest_init, recycled=year_recycled, lineage=k)
            else:
                # Get the harvest record for this year
                harvest = harvest_init.where(harvest_init.coords[nm.Fields.harvest_year] >= y, drop=True)
                harvest = harvest.where(harvest.coords[nm.Fields.harvest_year] == y, 0)
                harvest = harvest.assign_attrs({"lineage": k})
                m = Model(harvest=harvest, lineage=k)

            client = get_client()
            future = client.submit(m.run, key=k, priority=len(k))
            year_model_col.append(future)
            client.log_event("New Year Group", "Lineage: " + str(k))

        return year_model_col

    # def run_simulation(self):
    #     md = model_data.ModelData()
    #     harvest = md.data[nm.Tables.harvest]

    #     self.model_factory(harvest_init=harvest)

    #     return

    def run_simulation_dask(self):
        s = timeit.default_timer()
        md = model_data.ModelData()
        harvest = md.data[nm.Tables.harvest]

        years = harvest[nm.Fields.harvest_year]
        first_year = years.min().item()
        last_year = years.max().item()

        final_futures = Meta.model_factory(harvest_init=harvest)
        ac = as_completed(final_futures)

        year_ds_col_all = dict()
        year_ds_col_rec = dict()

        ds_all = None
        ds_rec = None

        for f in ac:
            r, r_futures = f.result()
            ykey = r.lineage[0]
            if ykey in year_ds_col_all:
                year_ds_col_all[ykey] = Model.aggregate_results(year_ds_col_all[ykey], r)
            else:
                year_ds_col_all[ykey] = r

            if ds_all is None:
                ds_all = r
            else:
                ds_all = Model.aggregate_results(ds_all, r)

            # Save the recycled materials on their own for reporting
            if len(r.lineage) > 1:
                if ykey in year_ds_col_rec:
                    year_ds_col_rec[ykey] = Model.aggregate_results(year_ds_col_rec[ykey], r)
                else:
                    year_ds_col_rec[ykey] = r

                if ds_rec is None:
                    ds_rec = r
                else:
                    ds_rec = Model.aggregate_results(ds_rec, r)

            if r_futures:
                ac.update(r_futures)

            f.release()  # This function is not actually documented, but it seems to be needed
            del f

        ds_all[nm.Fields.ccf] = harvest[nm.Fields.ccf]

        with Lock("plock"):
            print("===========================")
            print("Model run time", f"{(timeit.default_timer() - s) / 60} minutes")
            print("===========================")

        m = Model.make_results(ds_all, save=True)
        for y in year_ds_col_all:
            m = Model.make_results(year_ds_col_all[y], prefix=str(y), save=True)
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
        self.lineage = lineage

    def run(self):
        client = get_client()
        with Lock("plock"):
            print("Lineage:", self.lineage)

        if self.recycled is None:
            self.working_table = self.harvests.merge(self.md.ids, join="left", fill_value=0)
            # self.working_table = self.calculate_primary_product_mcg(self.working_table)
            self.working_table = self.calculate_end_use_products(self.working_table)
            self.working_table = self.calculate_products_in_use(self.working_table)
        else:
            self.working_table = self.recycled

        self.working_table = self.calculate_discarded_dispositions(self.working_table)
        self.working_table = self.calculate_dispositions(self.working_table)

        return self.working_table

    def calculate_primary_product_mcg(self, working_table):
        """Calculate the amounts of primary products (MgC) harvested in each year."""
        # TODO this needs reworked using the new ids system. The new system bypasses the intermedate
        # harvest conversion (timber->primary) but we still need that info for results.

        # Calculate timber products (CCF) by multiplying the harvest-to-timber ratio for each
        # timber product by the amount harvested that year.

        # timber_products = working_table.merge(self.md.data[nm.Tables.timber_products_ratios], join="left", fill_value=0.0)
        timber_products = working_table.merge(self.md.data[nm.Tables.timber_products], join="left", compat="override")
        timber_products[nm.Fields.timber_product_results] = timber_products[nm.Fields.timber_product_ratio] * timber_products[nm.Fields.ccf]

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

        # TODO we need the timber products in MTC for Annual Harvest and Timber Product Output
        # self.results.annual_timber_products = tmbr

        return primary_products

    def calculate_end_use_products(self, working_table):
        """Calculate the amount of end use products harvested in each year."""

        # Multiply the primary-to-end-use ratio for each end use product by the amount of the
        # corresponding primary product.
        # end_use = working_table.merge(self.md.data[nm.Tables.end_use_product_ratios], join="left", fill_value=0.0)
        # end_use[nm.Fields.end_use_results] = end_use[nm.Fields.end_use_ratio] * end_use[nm.Fields.primary_product_results]

        end_use = working_table
        end_use[nm.Fields.end_use_results] = working_table[nm.Fields.ccf] * working_table[nm.Fields.end_use_ratio_direct]

        return end_use

    @staticmethod
    def halflife_func(df):
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
        raise NotImplementedError()
        return

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

        # Don't take the whole dataframe and pass it to a mapped function, it destroys coordinates
        products_in_use = end_use[[nm.Fields.end_use_id, nm.Fields.end_use_halflife, nm.Fields.end_use_results, nm.Fields.end_use_sum]]
        products_in_use = products_in_use.groupby(nm.Fields.end_use_id).map(Model.halflife_func)

        end_use[nm.Fields.products_in_use] = products_in_use[nm.Fields.products_in_use]

        return end_use

    def calculate_discarded_dispositions(self, working_table):
        """Calculate the amount discarded during each inventory year and divide it up between the
        different dispositions (landfills, dumps, etc).
        """

        # Calculate the amount of each end use from year y that was discarded in year i
        # by subtracting the products in use from the amount of harvested product and
        # then subtracting the amount discarded in previous years.
        products_in_use = working_table

        piu_shift = products_in_use[nm.Fields.products_in_use].shift({nm.Fields.harvest_year: 1})
        end_use = products_in_use["end_use"].loc[dict(Year=products_in_use.coords["Year"].min())]
        piu_shift.loc[dict(Year=products_in_use.coords["Year"].min())] = end_use

        products_in_use[nm.Fields.discarded_products_results] = piu_shift - products_in_use[nm.Fields.products_in_use]

        # Zero out the stuff that was fuel.
        products_in_use[nm.Fields.discarded_products_results] = products_in_use[nm.Fields.discarded_products_results].where(
            products_in_use.data_vars[nm.Fields.fuel] == 0, 0
        )

        # Multiply the amount discarded this year by the disposition ratios to get the
        # amount that goes into landfills, dumps, etc, and then add these to the
        # discarded disposition totals for stuff discarded in year i.
        discard_ratios = self.md.data[nm.Tables.discard_destination_ratios]

        # TODO check here for DiscardTypeID recycle error
        products_in_use[nm.Fields.discard_dispositions] = xr.where(
            products_in_use[nm.Fields.discard_type_id] == 0,
            products_in_use[nm.Fields.discarded_products_results] * discard_ratios.loc[dict(DiscardTypeID=0)][nm.Fields.discard_destination_ratio],
            products_in_use[nm.Fields.discarded_products_results] * discard_ratios.loc[dict(DiscardTypeID=1)][nm.Fields.discard_destination_ratio],
        )

        return products_in_use

    @staticmethod
    def halflife_sum(df):
        # nb isn't giving a performance increase
        halflife = df[nm.Fields.halflife].item()
        if halflife == 0:
            df[nm.Fields.discard_remaining] = 0
        else:
            can_decay = df[nm.Fields.can_decay]
            l = len(can_decay)
            ox = np.zeros((l, l), dtype=np.float32)
            weightspace = np.array([math.exp(-math.log(2) * x / halflife) for x in range(l)])
            for h in range(l):
                v = can_decay[h].item()
                weights = weightspace[: l - h]
                o = np.zeros_like(can_decay)
                decayed = [v * w for w in weights]
                o[h:] = decayed
                ox[h] = o
            discard_remaining = np.sum(ox, axis=0)
            dd = xr.DataArray(discard_remaining, dims=df.dims, coords=df.coords).astype("float32")
            df[nm.Fields.discard_remaining] = dd
        return df

    def calculate_dispositions(self, working_table):
        """Calculate the amounts of discarded products that have been emitted, are still remaining,
        etc., for each inventory year.
        """

        # Calculate the amount in landfills that was discarded during this inventory year
        # that is subject to decay by multiplying the amount in the landfill by the
        # landfill-fixed-ratio. This will be used in later iterations of the i loop.
        destinations = self.md.data[nm.Tables.discard_destinations]
        # TODO make the ID lookup dynamic. For now we just need this done so hard code it
        # recycled_id = destinations.where(destinations == nm.Fields.recycled, drop=True)[nm.Fields.discard_destination_id].item()
        recycled_id = 1

        # Calculate the amount in landfills that was discarded during this inventory year
        # that is subject to decay by multiplying the amount in the landfill by the
        # landfill-fixed-ratio.
        dispositions = working_table
        dispositions[nm.Fields.fixed_ratio] = xr.where(
            working_table[nm.Fields.discard_type_id] == 0,
            destinations.loc[dict(DiscardTypeID=0)][nm.Fields.fixed_ratio],
            destinations.loc[dict(DiscardTypeID=1)][nm.Fields.fixed_ratio],
        )
        dispositions[nm.Fields.halflife] = xr.where(
            working_table[nm.Fields.discard_type_id] == 0,
            destinations.loc[dict(DiscardTypeID=0)][nm.Fields.halflife],
            destinations.loc[dict(DiscardTypeID=1)][nm.Fields.halflife],
        )
        dispositions[nm.Fields.can_decay] = dispositions[nm.Fields.discard_dispositions] * (1 - dispositions[nm.Fields.fixed_ratio])
        dispositions[nm.Fields.fixed] = dispositions[nm.Fields.discard_dispositions] * dispositions[nm.Fields.fixed_ratio]

        df_key = [
            nm.Fields.end_use_id,
            nm.Fields.discard_destination_id,
        ]

        recycled = dispositions.loc[dict(DiscardDestinationID=recycled_id)]
        recycled = recycled.drop_vars(nm.Fields.discard_destination_id)

        final_dispositions = dispositions

        final_dispositions[nm.Fields.discard_remaining] = xr.zeros_like(final_dispositions[nm.Fields.can_decay])

        # s = timeit.default_timer()
        # To get the discard remaining (present) amounts over time, we need to filter the dataframe to just the variables
        # at play, which are the can_decay and halflife primarily. We have to do this because dask can't chain groupby calls,
        # so we need to stack the grouping key. If we keep the whole dataset, this would reset the entire index which is
        # not desireable.
        dispositions = final_dispositions[[nm.Fields.halflife, nm.Fields.can_decay, nm.Fields.fixed, nm.Fields.discard_remaining]]
        dispositions = dispositions.stack(skey=df_key)

        dispositions = dispositions.groupby("skey").apply(Model.halflife_sum)

        # print("DISPOSITIONS APPLY", timeit.default_timer() - s)

        # The "could_decay" is the cumulative sum of "can_decay", which gives us the growing discard over time. This would be
        # the amount of product that could be present if it didn't decay. This minus the discard remaining results in the
        # emissions of that product.
        dispositions[nm.Fields.could_decay] = dispositions[nm.Fields.can_decay].groupby("skey").cumsum(dim=nm.Fields.harvest_year)

        # Unstack the key from the active table and write the new data back to the primary dataframe.
        final_dispositions[nm.Fields.could_decay] = dispositions.unstack()[nm.Fields.could_decay]
        final_dispositions[nm.Fields.discard_remaining] = dispositions.unstack()[nm.Fields.discard_remaining]

        # Calculate emissions from stuff discarded in year y by subracting the amount
        # remaining from the total amount that could decay.
        final_dispositions[nm.Fields.emitted] = final_dispositions[nm.Fields.could_decay] - final_dispositions[nm.Fields.discard_remaining]
        final_dispositions[nm.Fields.present] = final_dispositions[nm.Fields.discard_remaining]

        # Landfills are a bit different. Not all of it is subject to decay, so get the fixed amount and add it to present through time
        final_dispositions[nm.Fields.present] = final_dispositions[nm.Fields.present] + final_dispositions[nm.Fields.fixed]

        recycled_futures = None
        if len(self.lineage) <= recurse_limit and self.lineage[0] >= first_recycle_year:
            # For the new recycling, remove products assigned to be recycled and
            # begin a new simulation using the recycled products as "harvest" amounts
            # NOTE the below line doesn't work, it resets coords in a bad way. Hard coding selection.
            # recycled = dispositions.where(dispositions.coords[nm.Fields.discard_destination_id] == recycled_id, drop=True)
            recycled = final_dispositions.loc[dict(DiscardDestinationID=recycled_id)]
            recycled = recycled.drop_vars(nm.Fields.discard_destination_id)

            # Set the recycled material to be "in use" in the next year
            # TODO Check that recycling actually works after this, because this adds DiscardTypeID as a coordinate to products_in_use
            recycled[nm.Fields.products_in_use] = recycled[nm.Fields.can_decay]
            recycled[nm.Fields.harvest_year] = recycled[nm.Fields.harvest_year] + 1

            drop_key = [
                nm.Fields.discarded_products_results,
                nm.Fields.discard_dispositions,
                nm.Fields.fixed_ratio,
                nm.Fields.halflife,
                nm.Fields.can_decay,
                nm.Fields.fixed,
            ]
            recycled = recycled.drop_vars(drop_key)

            zero_key = [
                nm.Fields.ccf,
                nm.Fields.end_use_results,
                nm.Fields.end_use_sum,
            ]

            # Zero out harvest info because recycled material isn't harvested
            recycled[zero_key] = xr.zeros_like(recycled[zero_key])

            recycled_futures = Meta.model_factory(harvest_init=self.harvests, recycled=recycled, lineage=self.lineage)

        return final_dispositions, recycled_futures

    @staticmethod
    def aggregate_results(src_ds, new_ds):
        if src_ds.lineage[-1] > new_ds.lineage[-1]:
            return Model.aggregate_results(new_ds, src_ds)

        new_ds = new_ds.merge(src_ds, join="right", fill_value=0, compat="override")
        src_ds[nm.Fields.end_use_results] = src_ds[nm.Fields.end_use_results] + new_ds[nm.Fields.end_use_results]
        src_ds[nm.Fields.end_use_sum] = src_ds[nm.Fields.end_use_sum] + new_ds[nm.Fields.end_use_sum]
        src_ds[nm.Fields.products_in_use] = src_ds[nm.Fields.products_in_use] + new_ds[nm.Fields.products_in_use]
        src_ds[nm.Fields.discarded_products_results] = src_ds[nm.Fields.discarded_products_results] + new_ds[nm.Fields.discarded_products_results]
        src_ds[nm.Fields.discard_dispositions] = src_ds[nm.Fields.discard_dispositions] + new_ds[nm.Fields.discard_dispositions]
        src_ds[nm.Fields.can_decay] = src_ds[nm.Fields.can_decay] + new_ds[nm.Fields.can_decay]
        src_ds[nm.Fields.fixed] = src_ds[nm.Fields.fixed] + new_ds[nm.Fields.fixed]
        src_ds[nm.Fields.discard_remaining] = src_ds[nm.Fields.discard_remaining] + new_ds[nm.Fields.discard_remaining]
        src_ds[nm.Fields.could_decay] = src_ds[nm.Fields.could_decay] + new_ds[nm.Fields.could_decay]
        src_ds[nm.Fields.emitted] = src_ds[nm.Fields.emitted] + new_ds[nm.Fields.emitted]
        src_ds[nm.Fields.present] = src_ds[nm.Fields.present] + new_ds[nm.Fields.present]
        return src_ds

    @staticmethod
    def c_to_co2e(c: float) -> float:
        """Convert C to CO2e.

        Args:
            c (float): the C value to convert

        Returns:
            float: Units of CO2
        """
        return c * 44.0 / 12.0

    @staticmethod
    def make_results(ds, prefix="", save=False):

        C = nm.Fields.c
        MGC = nm.Fields.mgc
        CO2 = nm.Fields.co2
        P = nm.Fields.ppresent
        E = nm.Fields.eemitted
        CHANGE = nm.Fields.change

        final_e = ds[[nm.Fields.end_use_results, nm.Fields.products_in_use, nm.Fields.discarded_products_results]].sum(dim="EndUseID")
        final_d = ds[
            [
                nm.Fields.discard_dispositions,
                nm.Fields.can_decay,
                nm.Fields.fixed,
                nm.Fields.discard_remaining,
                nm.Fields.could_decay,
                nm.Fields.emitted,
                nm.Fields.present,
            ]
        ].sum(dim=["EndUseID", "DiscardDestinationID"])
        final = xr.merge([final_e, final_d])

        annual_harvest_and_timber = ds[[nm.Fields.ccf, nm.Fields.end_use_results]].sum(dim=nm.Fields.end_use_id)
        annual_harvest_and_timber = annual_harvest_and_timber.rename_vars(
            {nm.Fields.ccf: C(nm.Fields.ccf), nm.Fields.end_use_results: MGC(nm.Fields.end_use_results)}
        )

        compost_emitted = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=2)].sum(dim=nm.Fields.end_use_id)
        compost_emitted = Model.c_to_co2e(compost_emitted)
        compost_emitted.name = CO2(E(nm.Fields.composted))
        # compost_emitted = compost_emitted.cumsum()

        carbon_present_landfills = ds[nm.Fields.present].loc[dict(DiscardDestinationID=3)].sum(dim=nm.Fields.end_use_id)
        carbon_present_landfills.name = MGC(P(nm.Fields.landfills))
        carbon_emitted_landfills = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=3)].sum(dim=nm.Fields.end_use_id)
        carbon_emitted_landfills = Model.c_to_co2e(carbon_emitted_landfills)
        carbon_emitted_landfills.name = CO2(E(nm.Fields.landfills))

        carbon_present_dumps = ds[nm.Fields.present].loc[dict(DiscardDestinationID=4)].sum(dim=nm.Fields.end_use_id)
        carbon_present_dumps.name = MGC(P(nm.Fields.landfills))
        carbon_emitted_dumps = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=4)].sum(dim=nm.Fields.end_use_id)
        carbon_emitted_dumps = Model.c_to_co2e(carbon_emitted_dumps)
        carbon_emitted_dumps.name = CO2(E(nm.Fields.dumps))

        end_use_in_use = ds[nm.Fields.products_in_use].sum(dim=nm.Fields.end_use_id)
        end_use_in_use.name = MGC(nm.Fields.products_in_use)

        # TODO this is probably wrong (some should come from emitted probably...)
        burned_without_energy_capture = ds[nm.Fields.products_in_use].sum(dim=nm.Fields.end_use_id)
        burned_without_energy_capture = Model.c_to_co2e(burned_without_energy_capture)
        burned_without_energy_capture.name = CO2(E(nm.Fields.burned_wo_energy_capture))
        # burned_without_energy_capture_cum = burned_without_energy_capture.cumsum()
        # TODO burned_with_energy_capture
        # burned_with_energy_capture

        # TODO do we need to carry over the PIU to Emitted for fuels?
        fuel_carbon_emitted = ds[nm.Fields.products_in_use].where(ds.data_vars[nm.Fields.fuel] == 1, drop=True).sum(dim=nm.Fields.end_use_id)
        fuel_carbon_emitted = Model.c_to_co2e(fuel_carbon_emitted)
        fuel_carbon_emitted.name = CO2(E(nm.Fields.fuel))
        # fuel_carbon_emitted = fuel_carbon_emitted.cumsum()

        carbon_present_swds = carbon_present_landfills + carbon_present_dumps
        carbon_present_swds.name = MGC(P(nm.Fields.present))

        cumulative_carbon_stocks = xr.Dataset({nm.Fields.products_in_use: end_use_in_use, nm.Fields.swds: carbon_present_swds})
        cumulative_carbon_stocks[CHANGE(nm.Fields.products_in_use)] = cumulative_carbon_stocks[nm.Fields.products_in_use].diff(
            dim=nm.Fields.harvest_year
        )
        cumulative_carbon_stocks[CHANGE(nm.Fields.swds)] = cumulative_carbon_stocks[nm.Fields.swds].diff(dim=nm.Fields.harvest_year)

        if save:
            if len(prefix) > 1:
                prefix = prefix + "_"
            ds.to_dataframe().to_csv("output/" + prefix + "results.csv")
            final.to_dataframe().to_csv("output/" + prefix + "final.csv")
            annual_harvest_and_timber.to_dataframe().to_csv("output/" + prefix + "annual_harvest_and_timber_product_output.csv")
            cumulative_carbon_stocks[[CHANGE(nm.Fields.products_in_use), CHANGE(nm.Fields.swds)]].to_dataframe().to_csv(
                "output/" + prefix + "annual_net_change_carbon_stocks.csv"
            )
            burned_without_energy_capture.to_dataframe().to_csv("output/" + prefix + "burned_wo_energy_capture_emit.csv")
            compost_emitted.to_dataframe().to_csv("output/" + prefix + "total_composted_carbon_emitted.csv")
            cumulative_carbon_stocks[[nm.Fields.products_in_use, nm.Fields.swds]].to_dataframe().to_csv(
                "output/" + prefix + "total_cumulative_carbon_stocks.csv"
            )
            carbon_emitted_dumps.to_dataframe().to_csv("output/" + prefix + "total_dumps_carbon_emitted.csv")
            carbon_present_dumps.to_dataframe().to_csv("output/" + prefix + "total_dumps_carbon.csv")
            end_use_in_use.to_dataframe().to_csv("output/" + prefix + "total_end_use_products.csv")
            fuel_carbon_emitted.to_dataframe().to_csv("output/" + prefix + "total_fuelwood_carbon_emitted.csv")
            carbon_emitted_landfills.to_dataframe().to_csv("output/" + prefix + "total_landfills_carbon_emitted.csv")
            carbon_present_landfills.to_dataframe().to_csv("output/" + prefix + "total_landfills_carbon.csv")
        return
