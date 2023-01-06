import os
import sys
import tempfile
import timeit
import traceback
import zipfile
from io import BytesIO

import xarray as xr
import dask.config
from dask.distributed import Client, LocalCluster, Lock, as_completed, fire_and_forget, get_client, wait
from dask_cloudprovider.aws import FargateCluster
from dotenv import load_dotenv

from hwpccalc.hwpc import model, model_data
from hwpccalc.hwpc.names import Names as nm
from hwpccalc.utils import email, singleton
from hwpccalc.utils.s3_helper import S3Helper

load_dotenv()


class MetaModel(singleton.Singleton):
    """MetaModel is designed to be a singleton, so instance variables are set
    up here for scheduling, tracking, and resolving model runs.
    However, singletons aren't as useful on distirbuted environments, so this
    isn't strictly necessary any more.

    Attributes:
        start (timeit._Timer):
            The time MetaModel gets instantiated
        cluster (dask.distributed.LocalCluster):
            A dask cluster defined and provisioned at run time
        client (dask.Client):
            The dask client to attach to the cluster
        lock (dask.distributed.Lock):
            A syncroneous lock for printing output, mostly for debugging to guarantee
            print output order.
        _instance (MetaModel):
            The singleton object holder, inhereted.
    """

    def __new__(cls, *args, **kwargs):
        """MetaModel is designed to be a singleton, so instance variables are set
        up here for scheduling, tracking, and resolving model runs.
        However, singletons aren't as useful on distirbuted environments, so this
        isn't strictly necessary any more.
        """
        if MetaModel._instance is None:
            super().__new__(cls, args, kwargs)

            dask.config.set({"distributed.comm.timeouts.connect": "600s", "distributed.comm.timeouts.tcp": "600s"})

            MetaModel.start = timeit.default_timer()

            print("Provisioning cluster.")

            use_fargate_raw = os.getenv("DASK_USE_FARGATE")
            use_fargate = False

            if use_fargate_raw.lower().find("t") >= 0 or use_fargate_raw.lower().find("1") >= 0:
                use_fargate = True

            n_wrk = int(os.getenv("DASK_N_WORKERS"))

            if use_fargate:
                sch_cpu = int(os.getenv("DASK_SCEDULER_CPU"))
                sch_mem = int(os.getenv("DASK_SCEDULER_MEM"))
                wrk_cpu = int(os.getenv("DASK_WORKER_CPU"))
                wrk_mem = int(os.getenv("DASK_WORKER_MEM"))

                MetaModel.cluster = FargateCluster(
                    image="234659567514.dkr.ecr.us-west-2.amazonaws.com/hwpc-calc:worker",
                    scheduler_cpu=sch_cpu,
                    scheduler_mem=sch_mem,
                    worker_cpu=wrk_cpu,
                    worker_mem=wrk_mem,
                    n_workers=n_wrk,
                )

                # MetaModel.cluster.adapt(minimum=32, maximum=72, wait_count=60, target_duration="100s")
            else:
                MetaModel.cluster = LocalCluster(n_workers=n_wrk, processes=True, memory_limit=None)
                # MetaModel.cluster.adapt(minimum=8, maximum=24, wait_count=60, target_duration="120s")

            MetaModel.client = Client(
                # MetaModel.cluster, serializers=["dask", "cloudpickle", "pickle"], deserializers=["dask", "cloudpickle", "pickle"]
                MetaModel.cluster,
            )

            MetaModel.lock = Lock("plock", client=MetaModel.client)

            input_path = kwargs["input_path"]
            print("Meta Model:", input_path)
            output_path = input_path.replace("inputs", "outputs")
            run_name = kwargs["run_name"]

            md = model_data.ModelData(
                run_name=run_name,
                input_path=input_path,
                output_path=output_path,
            )

            MetaModel.client.publish_dataset(modeldata=md)

            with Lock("plock"):
                print("Cluster provisioned and Client attached.")

            print(MetaModel.client)

        return cls._instance

    def run_simulation(self):
        """ """
        sim_start = timeit.default_timer()
        # md = model_data.ModelData(path=nm.Output.input_path)
        # md = MetaModel.client.get_dataset("modeldata", default=model_data.ModelData(path=nm.Scenario.input_path))
        md = MetaModel.client.get_dataset("modeldata")
        harvest = md.data[nm.Tables.harvest]

        with Lock("plock"):
            print("Starting simluation.")

        final_futures = model.Model.model_factory(model_data_path=md.input_path, harvest_init=harvest)
        mod_jobs = as_completed(final_futures)
        year_ds_col_all = dict()
        year_ds_col_rec = dict()

        ds_all = None
        ds_rec = None

        with Lock("plock"):
            print("Futures created.")

        task_count = len(final_futures)

        # agg_jobs = as_completed([])

        for f in mod_jobs:
            r, r_futures = f.result()

            if r_futures is not None:
                task_count += len(r_futures)

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
                mod_jobs.update(r_futures)

            # f.release()
            # del f

        ds_all[nm.Fields.ccf] = harvest[nm.Fields.ccf]

        with Lock("plock"):
            print("===========================")
            print("Model run time:", f"{(timeit.default_timer() - MetaModel.start) / 60}", "minutes")
            print("Total tasks completed:", f"{task_count}")
            print("===========================")

        remote_ds_all = MetaModel.client.scatter(ds_all)

        # fire_and_forget make_results?
        res_jobs = list()

        try:
            # MetaModel.make_results(ds_all, prefix="comb", save=True)
            future = MetaModel.client.submit(MetaModel.make_results, remote_ds_all, prefix="comb", save=True)
            res_jobs.append(future)
        except Exception as e:
            print("ds_all_comb:", e)
            # raise e

        if ds_rec is not None:
            remote_ds_rec = MetaModel.client.scatter(ds_rec)
            try:
                # MetaModel.make_results(ds_rec, prefix="rec", save=True)
                future = MetaModel.client.submit(MetaModel.make_results, remote_ds_rec, prefix="rec", save=True)
                res_jobs.append(future)
            except Exception as e:
                print("ds_rec:", e)
                # raise e
            try:
                # MetaModel.make_results(ds_all, ds_rec, save=True)
                future = MetaModel.client.submit(MetaModel.make_results, remote_ds_all, remote_ds_rec, save=True)
                res_jobs.append(future)
            except Exception as e:
                print("ds_all:", e)
                # raise e
        else:
            # If there's no ds_rec, that either means there's no recycling, OR there hasn't
            # been any recycling so far (this run), OR ?
            try:
                # MetaModel.make_results(remote_ds_all, save=True)
                future = MetaModel.client.submit(MetaModel.make_results, remote_ds_all, save=True)
                res_jobs.append(future)
            except Exception as e:
                print("ds_all:", e)
                # raise e

        for y in year_ds_col_all:
            remote_year_ds_col_all = MetaModel.client.scatter(year_ds_col_all[y])

            try:
                # MetaModel.make_results(year_ds_col_all[y], prefix=str(y) + "_comb", save=True)
                future = MetaModel.client.submit(MetaModel.make_results, remote_year_ds_col_all, prefix=str(y) + "_comb", save=True)
                res_jobs.append(future)
            except Exception as e:
                print(str(y), "ds_all_comb:", e)
                # raise e

            if y in list(year_ds_col_rec.keys()):  # No recycling in the first year
                remote_year_ds_col_rec = MetaModel.client.scatter(year_ds_col_rec[y])
                try:
                    # MetaModel.make_results(year_ds_col_rec[y], prefix=str(y) + "_rec", save=True)
                    future = MetaModel.client.submit(MetaModel.make_results, remote_year_ds_col_rec, prefix=str(y) + "_rec", save=True)
                    res_jobs.append(future)
                except Exception as e:
                    print(str(y), "ds_rec:", e)
                    # raise e
                try:
                    # MetaModel.make_results(year_ds_col_all[y], year_ds_col_rec[y], prefix=str(y), save=True)
                    future = MetaModel.client.submit(MetaModel.make_results, remote_year_ds_col_all, remote_year_ds_col_rec, prefix=str(y), save=True)
                    res_jobs.append(future)
                except Exception as e:
                    print(str(y), "ds_all:", e)
                    # raise e
            else:
                try:
                    # MetaModel.make_results(year_ds_col_all[y], prefix=str(y), save=True)
                    future = MetaModel.client.submit(MetaModel.make_results, remote_year_ds_col_all, prefix=str(y), save=True)
                    res_jobs.append(future)
                except Exception as e:
                    print(str(y), "ds_all:", e)
                    # raise e

        with Lock("plock"):
            print("Waiting on result jobs.")

        wait(res_jobs)

        with Lock("plock"):
            print("===========================")
            print("Final run time", f"{(timeit.default_timer() - MetaModel.start) / 60} minutes")
            print("===========================")

        # We need a couple things for the email that gets sent, after the cluster might be closed.
        ret_dict = {
            "email_address": md.scenario_info["email"],
            "user_string": md.scenario_info["user_string"],
            "scenario_name": md.scenario_info["scenario_name"],
        }

        return ret_dict

    @staticmethod
    def aggregate_results(src_ds, new_ds):
        src_ds, new_ds = xr.align(src_ds, new_ds, join="outer", fill_value=0)

        src_ds[nm.Fields.end_use_products] = src_ds[nm.Fields.end_use_products] + new_ds[nm.Fields.end_use_products]
        src_ds[nm.Fields.end_use_available] = src_ds[nm.Fields.end_use_available] + new_ds[nm.Fields.end_use_available]
        src_ds[nm.Fields.products_in_use] = src_ds[nm.Fields.products_in_use] + new_ds[nm.Fields.products_in_use]
        src_ds[nm.Fields.discarded_products] = src_ds[nm.Fields.discarded_products] + new_ds[nm.Fields.discarded_products]
        src_ds[nm.Fields.discarded_dispositions] = src_ds[nm.Fields.discarded_dispositions] + new_ds[nm.Fields.discarded_dispositions]
        src_ds[nm.Fields.can_decay] = src_ds[nm.Fields.can_decay] + new_ds[nm.Fields.can_decay]
        src_ds[nm.Fields.fixed] = src_ds[nm.Fields.fixed] + new_ds[nm.Fields.fixed]
        src_ds[nm.Fields.discarded_remaining] = src_ds[nm.Fields.discarded_remaining] + new_ds[nm.Fields.discarded_remaining]
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
    def make_results(ds: xr.Dataset, rec_ds: xr.Dataset = None, prefix: str = "", save=False):

        client = get_client()
        md = client.get_dataset("modeldata")

        C = nm.Fields.c
        MGC = nm.Fields.mgc
        CO2 = nm.Fields.co2
        P = nm.Fields.ppresent
        E = nm.Fields.eemitted
        CHANGE = nm.Fields.change

        nonrec_piu = None
        if rec_ds:
            ds, rec_ds = xr.align(ds, rec_ds, join="left", fill_value=0)
            nonrec_piu = ds[nm.Fields.products_in_use] - rec_ds[nm.Fields.products_in_use]

        final_e = ds[[nm.Fields.end_use_products, nm.Fields.products_in_use, nm.Fields.discarded_products]].sum(dim="EndUseID")
        final_d = ds[
            [
                nm.Fields.discarded_dispositions,
                nm.Fields.can_decay,
                nm.Fields.fixed,
                nm.Fields.discarded_remaining,
                nm.Fields.could_decay,
                nm.Fields.emitted,
                nm.Fields.present,
            ]
        ].sum(dim=[nm.Fields.end_use_id, nm.Fields.discard_destination_id])
        final = xr.merge([final_e, final_d])

        annual_harvest_and_timber = ds[[nm.Fields.ccf, nm.Fields.end_use_products]].sum(dim=nm.Fields.end_use_id)
        annual_harvest_and_timber = annual_harvest_and_timber.rename_vars(
            {nm.Fields.ccf: C(nm.Fields.ccf), nm.Fields.end_use_products: MGC(nm.Fields.end_use_products)}
        )

        compost_emitted = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=2)].sum(dim=nm.Fields.end_use_id)
        compost_emitted = MetaModel.c_to_co2e(compost_emitted)
        compost_emitted.name = CO2(E(nm.Fields.composted))
        compost_emitted = compost_emitted.drop_vars(nm.Fields.discard_destination_id)

        carbon_present_landfills = ds[nm.Fields.present].loc[dict(DiscardDestinationID=3)].sum(dim=nm.Fields.end_use_id)
        carbon_present_landfills.name = MGC(P(nm.Fields.landfills))
        carbon_present_landfills = carbon_present_landfills.drop_vars(nm.Fields.discard_destination_id)
        carbon_emitted_landfills = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=3)].sum(dim=nm.Fields.end_use_id)
        carbon_emitted_landfills = MetaModel.c_to_co2e(carbon_emitted_landfills)
        carbon_emitted_landfills.name = CO2(E(nm.Fields.landfills))
        carbon_emitted_landfills = carbon_emitted_landfills.drop_vars(nm.Fields.discard_destination_id)

        carbon_present_dumps = ds[nm.Fields.present].loc[dict(DiscardDestinationID=4)].sum(dim=nm.Fields.end_use_id)
        carbon_present_dumps.name = MGC(P(nm.Fields.dumps))
        carbon_present_dumps = carbon_present_dumps.drop_vars(nm.Fields.discard_destination_id)
        carbon_emitted_dumps = ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=4)].sum(dim=nm.Fields.end_use_id)
        carbon_emitted_dumps = MetaModel.c_to_co2e(carbon_emitted_dumps)
        carbon_emitted_dumps.name = CO2(E(nm.Fields.dumps))
        carbon_emitted_dumps = carbon_emitted_dumps.drop_vars(nm.Fields.discard_destination_id)

        fuel_carbon_emitted = (
            ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=0)].where(ds.data_vars[nm.Fields.fuel] == 1, drop=True).sum(dim=nm.Fields.end_use_id)
        )
        fuel_carbon_emitted = MetaModel.c_to_co2e(fuel_carbon_emitted)
        fuel_carbon_emitted.name = CO2(E(nm.Fields.fuel))
        fuel_carbon_emitted = fuel_carbon_emitted.drop_vars(nm.Fields.discard_destination_id)

        if rec_ds:
            end_use_in_use_nr = nonrec_piu.sum(dim=nm.Fields.end_use_id)
            end_use_in_use_nr.name = MGC("new_" + nm.Fields.products_in_use)
            end_use_in_use_r = rec_ds[nm.Fields.products_in_use].sum(dim=nm.Fields.end_use_id)
            end_use_in_use_r.name = MGC("reused_" + nm.Fields.products_in_use)

            end_use_in_use = xr.Dataset({end_use_in_use_nr.name: end_use_in_use_nr, end_use_in_use_r.name: end_use_in_use_r})
        else:
            end_use_in_use = ds[nm.Fields.products_in_use].sum(dim=nm.Fields.end_use_id)
            end_use_in_use.name = MGC(nm.Fields.products_in_use)

        burned_without_energy_capture = (
            ds[nm.Fields.emitted].loc[dict(DiscardDestinationID=0)].where(ds.data_vars[nm.Fields.fuel] == 0, drop=True).sum(dim=nm.Fields.end_use_id)
        )
        burned_without_energy_capture = MetaModel.c_to_co2e(burned_without_energy_capture)
        burned_without_energy_capture.name = CO2(E(nm.Fields.burned_wo_energy_capture))
        burned_without_energy_capture = burned_without_energy_capture.drop_vars(nm.Fields.discard_destination_id)

        # TODO discard_burned_with_energy_capture
        burned_with_energy_capture = fuel_carbon_emitted  # TODO + discard_burned_with_energy_capture

        carbon_present_swds = carbon_present_landfills + carbon_present_dumps
        carbon_present_swds.name = MGC(P(nm.Fields.present))

        if rec_ds:
            cumulative_carbon_stocks = xr.Dataset(
                {
                    "new_" + MGC(nm.Fields.products_in_use): end_use_in_use[end_use_in_use_nr.name],
                    "reused_" + MGC(nm.Fields.products_in_use): end_use_in_use[end_use_in_use_r.name],
                    MGC(nm.Fields.swds): carbon_present_swds,
                }
            )
            cumulative_carbon_stocks["new_" + MGC(CHANGE(nm.Fields.products_in_use))] = cumulative_carbon_stocks[
                "new_" + MGC(nm.Fields.products_in_use)
            ].diff(
                dim=nm.Fields.harvest_year,
            )
            cumulative_carbon_stocks["reused_" + MGC(CHANGE(nm.Fields.products_in_use))] = cumulative_carbon_stocks[
                "reused_" + MGC(nm.Fields.products_in_use)
            ].diff(
                dim=nm.Fields.harvest_year,
            )
        else:
            cumulative_carbon_stocks = xr.Dataset({MGC(nm.Fields.products_in_use): end_use_in_use, MGC(nm.Fields.swds): carbon_present_swds})
            cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.products_in_use))] = cumulative_carbon_stocks[MGC(nm.Fields.products_in_use)].diff(
                dim=nm.Fields.harvest_year,
            )
        cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.swds))] = cumulative_carbon_stocks[MGC(nm.Fields.swds)].diff(dim=nm.Fields.harvest_year)
        cumulative_carbon_stocks = cumulative_carbon_stocks.fillna(0)

        # totalYearlyNetChange PDF
        if rec_ds:
            cumulative_stock_change = (
                cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.swds))]
                + cumulative_carbon_stocks["new_" + MGC(CHANGE(nm.Fields.products_in_use))]
                + cumulative_carbon_stocks["reused_" + MGC(CHANGE(nm.Fields.products_in_use))]
            )
            cumulative_stock_change.name = MGC(CHANGE(nm.Fields.present))
        else:
            cumulative_stock_change = (
                cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.swds))] + cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.products_in_use))]
            )
            cumulative_stock_change.name = MGC(CHANGE(nm.Fields.present))
        # totalSelectedNetChange PDF
        cumulative_selected_stock_change = cumulative_carbon_stocks.sel(Year=cumulative_carbon_stocks[nm.Fields.harvest_year] % 5 == 0)

        emitted_w_ec = fuel_carbon_emitted
        emitted_w_ec.name = CO2(nm.Fields.emitted_with_energy_capture)

        emitted_wo_ec = compost_emitted + carbon_emitted_landfills + carbon_emitted_dumps + burned_without_energy_capture
        emitted_wo_ec.name = CO2(nm.Fields.emitted_wo_energy_capture)

        if rec_ds:
            big_four = xr.Dataset(
                {
                    "new_" + CO2(P(nm.Fields.products_in_use)): MetaModel.c_to_co2e(end_use_in_use_nr),
                    "reused_" + CO2(P(nm.Fields.products_in_use)): MetaModel.c_to_co2e(end_use_in_use_r),
                    CO2(P(nm.Fields.swds)): MetaModel.c_to_co2e(carbon_present_swds),
                    CO2(E(nm.Fields.emitted_with_energy_capture)): emitted_w_ec,
                    CO2(E(nm.Fields.emitted_wo_energy_capture)): emitted_wo_ec,
                }
            )
        else:
            big_four = xr.Dataset(
                {
                    "new_" + CO2(P(nm.Fields.products_in_use)): MetaModel.c_to_co2e(end_use_in_use),
                    CO2(P(nm.Fields.swds)): MetaModel.c_to_co2e(carbon_present_swds),
                    CO2(E(nm.Fields.emitted_with_energy_capture)): emitted_w_ec,
                    CO2(E(nm.Fields.emitted_wo_energy_capture)): emitted_wo_ec,
                }
            )
        emitted_all = xr.Dataset(
            {
                CO2(E(nm.Fields.fuel)): fuel_carbon_emitted,
                CO2(E(nm.Fields.composted)): compost_emitted,
                CO2(E(nm.Fields.dumps)): carbon_emitted_dumps,
                CO2(E(nm.Fields.landfills)): carbon_emitted_landfills,
            }
        )
        if rec_ds:
            carbon_present_distinct_swds = xr.Dataset(
                {
                    MGC(P(nm.Fields.dumps)): carbon_present_dumps,
                    MGC(P(nm.Fields.landfills)): carbon_present_landfills,
                    "new_" + MGC(nm.Fields.products_in_use): end_use_in_use_nr,
                    "reused_" + MGC(nm.Fields.products_in_use): end_use_in_use_r,
                }
            )
        else:
            carbon_present_distinct_swds = xr.Dataset(
                {
                    MGC(P(nm.Fields.dumps)): carbon_present_dumps,
                    MGC(P(nm.Fields.landfills)): carbon_present_landfills,
                    MGC(nm.Fields.products_in_use): end_use_in_use,
                }
            )
        carbon_emitted_distinct_swds = xr.Dataset(
            {CO2(E(nm.Fields.dumps)): carbon_emitted_dumps, CO2(E(nm.Fields.landfills)): carbon_emitted_landfills}
        )

        # totalYearlyDispositions PDF
        if rec_ds:
            mega_table = xr.Dataset(
                {
                    CO2(nm.Fields.emitted_with_energy_capture): emitted_w_ec,
                    CO2(CHANGE(nm.Fields.emitted_with_energy_capture)): emitted_w_ec.diff(dim=nm.Fields.harvest_year),
                    CO2(nm.Fields.emitted_wo_energy_capture): emitted_wo_ec,
                    CO2(CHANGE(nm.Fields.emitted_wo_energy_capture)): emitted_wo_ec.diff(dim=nm.Fields.harvest_year),
                    "reused_" + MGC(nm.Fields.products_in_use): cumulative_carbon_stocks["reused_" + MGC(nm.Fields.products_in_use)],
                    "reused_" + MGC(CHANGE(nm.Fields.products_in_use)): cumulative_carbon_stocks["reused_" + MGC(CHANGE(nm.Fields.products_in_use))],
                    "new_" + MGC(nm.Fields.products_in_use): cumulative_carbon_stocks["new_" + MGC(nm.Fields.products_in_use)],
                    "new_" + MGC(CHANGE(nm.Fields.products_in_use)): cumulative_carbon_stocks["new_" + MGC(CHANGE(nm.Fields.products_in_use))],
                    MGC(nm.Fields.swds): cumulative_carbon_stocks[MGC(nm.Fields.swds)],
                    MGC(CHANGE(nm.Fields.swds)): cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.swds))],
                    MGC(nm.Fields.present): cumulative_carbon_stocks[MGC(nm.Fields.swds)]
                    + cumulative_carbon_stocks["reused_" + MGC(nm.Fields.products_in_use)]
                    + cumulative_carbon_stocks["new_" + MGC(nm.Fields.products_in_use)],
                    MGC(CHANGE(nm.Fields.present)): cumulative_stock_change,
                }
            )
        else:
            mega_table = xr.Dataset(
                {
                    CO2(nm.Fields.emitted_with_energy_capture): emitted_w_ec,
                    CO2(CHANGE(nm.Fields.emitted_with_energy_capture)): emitted_w_ec.diff(dim=nm.Fields.harvest_year),
                    CO2(nm.Fields.emitted_wo_energy_capture): emitted_wo_ec,
                    CO2(CHANGE(nm.Fields.emitted_wo_energy_capture)): emitted_wo_ec.diff(dim=nm.Fields.harvest_year),
                    MGC(nm.Fields.products_in_use): cumulative_carbon_stocks[MGC(nm.Fields.products_in_use)],
                    MGC(CHANGE(nm.Fields.products_in_use)): cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.products_in_use))],
                    MGC(nm.Fields.swds): cumulative_carbon_stocks[MGC(nm.Fields.swds)],
                    MGC(CHANGE(nm.Fields.swds)): cumulative_carbon_stocks[MGC(CHANGE(nm.Fields.swds))],
                    MGC(nm.Fields.present): cumulative_carbon_stocks[MGC(nm.Fields.swds)] + cumulative_carbon_stocks[MGC(nm.Fields.products_in_use)],
                    MGC(CHANGE(nm.Fields.present)): cumulative_stock_change,
                }
            )

        # totalSelectedDispositions PDF
        mega_selected_table = mega_table.sel(Year=cumulative_carbon_stocks[nm.Fields.harvest_year] % 5 == 0)

        if save:
            zip_buffer = BytesIO()

            zip = zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_STORED, allowZip64=False)
            # with tempfile.TemporaryFile() as temp:
            # harvest_data.to_csv(temp)
            # temp.seek(0)
            # self.zip.writestr('harvest_data.csv', temp.read(), compress_type=zipfile.ZIP_STORED)
            if len(prefix) > 1:
                prefix = prefix + "_"
            with tempfile.TemporaryFile() as temp:
                ds.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "results.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                final.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "final.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                annual_harvest_and_timber.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "annual_harvest_and_timber_product_output.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                if rec_ds:
                    cumulative_carbon_stocks[
                        [
                            "new_" + MGC(CHANGE(nm.Fields.products_in_use)),
                            "reused_" + MGC(CHANGE(nm.Fields.products_in_use)),
                            MGC(CHANGE(nm.Fields.swds)),
                        ]
                    ].to_dataframe().to_csv(temp)
                else:
                    cumulative_carbon_stocks[[MGC(CHANGE(nm.Fields.products_in_use)), MGC(CHANGE(nm.Fields.swds))]].to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "annual_net_change_carbon_stocks.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                burned_without_energy_capture.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "burned_wo_energy_capture_emit.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                burned_with_energy_capture.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "burned_w_energy_capture_emit.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                compost_emitted.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_composted_carbon_emitted.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                if rec_ds:
                    cumulative_carbon_stocks[
                        ["new_" + MGC(nm.Fields.products_in_use), "reused_" + MGC(nm.Fields.products_in_use), MGC(nm.Fields.swds)]
                    ].to_dataframe().to_csv(temp)
                else:
                    cumulative_carbon_stocks[[MGC(nm.Fields.products_in_use), MGC(nm.Fields.swds)]].to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_cumulative_carbon_stocks.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                carbon_emitted_dumps.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_dumps_carbon_emitted.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                carbon_present_dumps.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_dumps_carbon.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                end_use_in_use.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_end_use_products.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                fuel_carbon_emitted.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_fuelwood_carbon_emitted.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                carbon_emitted_landfills.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_landfills_carbon_emitted.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                carbon_present_landfills.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_landfills_carbon.csv", temp.read(), compress_type=zipfile.ZIP_STORED)

            # Flashy page outputs
            with tempfile.TemporaryFile() as temp:
                big_four.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "big_four.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                emitted_all.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "emitted_all.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                carbon_present_distinct_swds.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "carbon_present_distinct_swds.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                carbon_emitted_distinct_swds.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "carbon_emitted_distinct_swds.csv", temp.read(), compress_type=zipfile.ZIP_STORED)

            # PDF table outputs
            with tempfile.TemporaryFile() as temp:
                cumulative_stock_change.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_yearly_net_change.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                cumulative_selected_stock_change.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_selected_net_change.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                mega_table.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_yearly_dispositions.csv", temp.read(), compress_type=zipfile.ZIP_STORED)
            with tempfile.TemporaryFile() as temp:
                mega_selected_table.to_dataframe().to_csv(temp)
                temp.seek(0)
                zip.writestr(prefix + "total_selected_dispositions.csv", temp.read(), compress_type=zipfile.ZIP_STORED)

            zip.close()
            zip_buffer.seek(0)
            S3Helper.upload_file(zip_buffer, "hwpc-output", md.output_path + "/results/" + prefix + md.run_name + ".zip")

        return
