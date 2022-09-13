import math
import timeit

import cloudpickle
import numpy as np
import xarray as xr
from dask.distributed import Lock, get_client

try:
    from hwpc.names import Names as nm
except:
    import os

    p = os.path.join(os.path.dirname(__file__), "..")
    import sys

    sys.path.append(p)
    from hwpc.names import Names as nm


recurse_limit = 0
first_recycle_year = 1980  # TODO make this dynamic


class Model(object):
    @staticmethod
    def model_factory(model_data=None, harvest_init=None, lineage=None, recycled=None):
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
                harvest = harvest_init
            else:
                # Get the harvest record for this year
                harvest = harvest_init.where(harvest_init.coords[nm.Fields.harvest_year] >= y, drop=True)
                harvest = harvest.where(harvest.coords[nm.Fields.harvest_year] == y, 0)
                harvest = harvest.assign_attrs({"lineage": k})
                year_recycled = None

            client = get_client()
            m = Model.run
            future = client.submit(m, md=model_data, harvests=harvest, recycled=year_recycled, lineage=k, key=k, priority=len(k))
            year_model_col.append(future)
            client.log_event("New Year Group", "Lineage: " + str(k))

        return year_model_col

    @staticmethod
    def run(md=None, harvests=None, recycled=None, lineage=None):
        client = get_client()
        with Lock("plock"):
            print("Lineage:", lineage)

        if recycled is None:
            working_table = harvests.merge(md.ids, join="left", fill_value=0)
            working_table = Model.calculate_end_use_products(working_table)
            working_table = Model.calculate_products_in_use(md, working_table)
        else:
            working_table = recycled

        working_table = Model.calculate_discarded_dispositions(md, working_table)
        working_table = Model.calculate_dispositions(harvests, lineage, md, working_table)

        return working_table

    @staticmethod
    def calculate_end_use_products(working_table):
        """Calculate the amount of end use products harvested in each year."""

        # Multiply the primary-to-end-use ratio for each end use product by the amount of the
        # corresponding primary product.
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

    @staticmethod
    def calculate_products_in_use(md, working_table):
        """Calculate the amount of end use products from each vintage year that are still in use
        during each inventory year.
        """
        # Make sure the rows are ascending to do the half life. Don't do this inplace
        # end_use = end_use.sort_values(by=nm.Fields.harvest_year)
        end_use = working_table.merge(
            md.data[nm.Tables.end_use_products],
            join="left",
            compat="override",
            fill_value=0,
        )

        loss = 1 - float(md.data[nm.Tables.loss_factor].columns.values[0])
        end_use[nm.Fields.end_use_sum] = xr.where(
            end_use[nm.Fields.discard_type_id] == 0, end_use[nm.Fields.end_use_results], end_use[nm.Fields.end_use_results] * loss
        )

        # Don't take the whole dataframe and pass it to a mapped function, it destroys coordinates
        products_in_use = end_use[[nm.Fields.end_use_id, nm.Fields.end_use_halflife, nm.Fields.end_use_results, nm.Fields.end_use_sum]]
        products_in_use = products_in_use.groupby(nm.Fields.end_use_id).map(Model.halflife_func)

        end_use[nm.Fields.products_in_use] = products_in_use[nm.Fields.products_in_use]

        return end_use

    @staticmethod
    def calculate_discarded_dispositions(md, working_table):
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
        discard_ratios = md.data[nm.Tables.discard_destination_ratios]

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

    @staticmethod
    def calculate_dispositions(harvests, lineage, md, working_table):
        """Calculate the amounts of discarded products that have been emitted, are still remaining,
        etc., for each inventory year.
        """

        # Calculate the amount in landfills that was discarded during this inventory year
        # that is subject to decay by multiplying the amount in the landfill by the
        # landfill-fixed-ratio. This will be used in later iterations of the i loop.
        destinations = md.data[nm.Tables.discard_destinations]
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
        if len(lineage) <= recurse_limit and lineage[0] >= first_recycle_year:
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

            recycled_futures = Model.model_factory(model_data=md, harvest_init=harvests, recycled=recycled, lineage=lineage)

        return final_dispositions, recycled_futures


# if __name__ == "__main__":
#     print("Local test")
