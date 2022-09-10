import timeit
from dask.distributed import Client, LocalCluster, as_completed, Lock
from dask_cloudprovider.aws import FargateCluster
import traceback
import xarray as xr

from hwpc import model
from hwpc import model_data
from hwpc.names import Names as nm

from utils import singleton


class MetaModel(singleton.Singleton):
    def __new__(cls, *args, **kwargs):
        if MetaModel._instance is None:
            super().__new__(cls, args, kwargs)

            MetaModel.cluster = LocalCluster(n_workers=8, processes=True)

            # Meta.cluster = FargateCluster(
            #     image = "234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:test",
            #     scheduler_cpu = 4096,
            #     scheduler_mem = 8192,
            #     worker_cpu = 1024,
            #     worker_nthreads = 2,
            #     worker_mem = 2048,
            #     n_workers = 8
            # )

            MetaModel.cluster.adapt(minimum=8, maximum=30, wait_count=6)

            MetaModel.client = Client(MetaModel.cluster)

            MetaModel.lock = Lock("plock")

            print(MetaModel.client)

        return cls._instance

    def run_simulation(self):
        s = timeit.default_timer()
        md = model_data.ModelData()
        harvest = md.data[nm.Tables.harvest]

        years = harvest[nm.Fields.harvest_year]

        final_futures = model.Model.model_factory(model_data=md, harvest_init=harvest)
        ac = as_completed(final_futures)

        year_ds_col_all = dict()
        year_ds_col_rec = dict()

        ds_all = None
        ds_rec = None

        try:
            for f in ac:
                r, r_futures = f.result()
                ykey = r.lineage[0]
                if ykey in year_ds_col_all:
                    year_ds_col_all[ykey] = MetaModel.aggregate_results(year_ds_col_all[ykey], r)
                else:
                    year_ds_col_all[ykey] = r

                if ds_all is None:
                    ds_all = r
                else:
                    ds_all = MetaModel.aggregate_results(ds_all, r)

                # Save the recycled materials on their own for reporting
                if len(r.lineage) > 1:
                    if ykey in year_ds_col_rec:
                        year_ds_col_rec[ykey] = MetaModel.aggregate_results(year_ds_col_rec[ykey], r)
                    else:
                        year_ds_col_rec[ykey] = r

                    if ds_rec is None:
                        ds_rec = r
                    else:
                        ds_rec = MetaModel.aggregate_results(ds_rec, r)

                if r_futures:
                    ac.update(r_futures)

                f.release()  # This function is not actually documented, but it seems to be needed
                del f

            ds_all[nm.Fields.ccf] = harvest[nm.Fields.ccf]

            with Lock("plock"):
                print("===========================")
                print("Model run time", f"{(timeit.default_timer() - s) / 60} minutes")
                print("===========================")

            m = MetaModel.make_results(ds_all, save=True)
            for y in year_ds_col_all:
                m = MetaModel.make_results(year_ds_col_all[y], prefix=str(y), save=True)
        except Exception as e:
            MetaModel.cluster.close()
            print(e)
            traceback.print_exc()
        return

    @staticmethod
    def aggregate_results(src_ds, new_ds):
        if src_ds.lineage[-1] > new_ds.lineage[-1]:
            return MetaModel.aggregate_results(new_ds, src_ds)

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
        compost_emitted = MetaModel.c_to_co2e(compost_emitted)
        compost_emitted.name = CO2(E(nm.Fields.composted))
        # compost_emitted = compost_emitted.cumsum()

        carbon_present_landfills = ds[nm.Fields.present].loc[dict(DiscardDestinationID=3)].sum(dim=nm.Fields.end_use_id)
        carbon_present_landfills.name = MGC(P(nm.Fields.landfills))
        carbon_emitted_landfills = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=3)].sum(dim=nm.Fields.end_use_id)
        carbon_emitted_landfills = MetaModel.c_to_co2e(carbon_emitted_landfills)
        carbon_emitted_landfills.name = CO2(E(nm.Fields.landfills))

        carbon_present_dumps = ds[nm.Fields.present].loc[dict(DiscardDestinationID=4)].sum(dim=nm.Fields.end_use_id)
        carbon_present_dumps.name = MGC(P(nm.Fields.landfills))
        carbon_emitted_dumps = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=4)].sum(dim=nm.Fields.end_use_id)
        carbon_emitted_dumps = MetaModel.c_to_co2e(carbon_emitted_dumps)
        carbon_emitted_dumps.name = CO2(E(nm.Fields.dumps))

        end_use_in_use = ds[nm.Fields.products_in_use].sum(dim=nm.Fields.end_use_id)
        end_use_in_use.name = MGC(nm.Fields.products_in_use)

        # TODO this is probably wrong (some should come from emitted probably...)
        burned_without_energy_capture = ds[nm.Fields.products_in_use].sum(dim=nm.Fields.end_use_id)
        burned_without_energy_capture = MetaModel.c_to_co2e(burned_without_energy_capture)
        burned_without_energy_capture.name = CO2(E(nm.Fields.burned_wo_energy_capture))
        # burned_without_energy_capture_cum = burned_without_energy_capture.cumsum()
        # TODO burned_with_energy_capture
        # burned_with_energy_capture

        # TODO do we need to carry over the PIU to Emitted for fuels?
        fuel_carbon_emitted = ds[nm.Fields.products_in_use].where(ds.data_vars[nm.Fields.fuel] == 1, drop=True).sum(dim=nm.Fields.end_use_id)
        fuel_carbon_emitted = MetaModel.c_to_co2e(fuel_carbon_emitted)
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
