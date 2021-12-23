from datetime import timedelta
import math
import numpy as np
import pandas as pd
import timeit
# import dask.dataframe as dd
# from dask.multiprocessing import get
import multiprocessing as mp
from functools import reduce

from hwpc import model_data
from hwpc import results
from hwpc.names import Names as nm

# pandarallel.initialize()

class Model(object):

    def __init__(self) -> None:
        super().__init__()

        self.md = model_data.ModelData()

        self.harvests = self.md.data[nm.Tables.harvest]
        self.harvests = self.harvests.sort_values(by=nm.Fields.harvest_year)
        

        self.timber_product_ratios = self.md.data[nm.Tables.timber_products_data]
        self.primary_product_ratios = self.md.data[nm.Tables.primary_product_ratios]
        
        self.end_use_ratios = self.md.data[nm.Tables.end_use_ratios]
        self.end_use_products = self.md.data[nm.Tables.end_use_products]
        
        self.discarded_disposition_ratios = self.md.data[nm.Tables.discard_disposition_ratios]

        # the amount of product that is not lost
        self.end_use_loss_factor = 0.92

        # default percent of product that is burned with energy capture
        self.default_burned_energy_capture = 0

        self.results = results.Results()

    def run(self):
        
        self.calculate_primary_product_mcg()
        self.calculate_end_use_products()
        self.calculate_products_in_use()
        self.calculate_discarded_dispositions()
        self.calculate_dispositions()
        self.calculate_fuel_burned()
        self.calculate_discarded_burned()
        self.summarize()
        self.convert_c02_e()
        self.final_table()

        self.results.save_results()
        self.results.save_total_dispositions()

        return

    def calculate_primary_product_mcg(self):
        """Calculate the amounts of primary products (MgC) harvested in each year.
        """

        # Calculate timber products (CCF) by multiplying the harvest-to-timber ratio for each
        # timber product by the amount harvested that year.

        # TODO convert mgc I guess?   
        # IF MgC, convert to CCF. The rest of the model uses CCF.

        timber_products = self.harvests.merge(self.timber_product_ratios, how='outer')
        timber_products[nm.Fields.timber_product_results] = timber_products[nm.Fields.timber_product_ratio] * timber_products[nm.Fields.ccf]

        timber_products = timber_products.dropna()
        timber_products = timber_products.sort_values(by=[nm.Fields.harvest_year, nm.Fields.timber_product_id])

        self.results.timber_products = timber_products
        self.results.harvests = self.harvests

        # Calculate primary products (CCF) by multiplying the timber-to-primary ratio for each 
        # primary product by the amount of the corresponding timber product. Then convert to MgC
        # by multiplying by the CCF-to-MgC ratio for that primary product.
        
        # Append the timber product id to the primary product table
        primary_products = self.primary_product_ratios
        primary_products[nm.Fields.timber_product_id] = primary_products[nm.Fields.primary_product_id].map(self.md.primary_product_to_timber_product)

        primary_products = timber_products.merge(primary_products, how='outer', on=[nm.Fields.harvest_year, nm.Fields.timber_product_id])
        primary_products[nm.Fields.primary_product_results] = primary_products[nm.Fields.primary_product_ratio] * primary_products[nm.Fields.timber_product_results]

        primary_products = primary_products.dropna()
        primary_products = primary_products.sort_values(by=[nm.Fields.harvest_year, nm.Fields.timber_product_id, nm.Fields.primary_product_id])

        self.results.primary_products = primary_products
        self.results.working_table = primary_products

        return

    def calculate_end_use_products(self):
        """Calculate the amount of end use products harvested in each year.
        """

        # Multiply the primary-to-end-use ratio for each end use product by the amount of the
        # corresponding primary product.

        end_use = self.end_use_ratios
        end_use[nm.Fields.primary_product_id] = end_use[nm.Fields.end_use_id].map(self.md.end_use_to_primary_product)

        end_use = self.results.working_table.merge(end_use, how='outer', on=[nm.Fields.harvest_year, nm.Fields.primary_product_id])
        end_use[nm.Fields.end_use_results] = end_use[nm.Fields.end_use_ratio] * end_use[nm.Fields.primary_product_results]

        end_use = end_use.dropna()

        # Add a year to account for the shift
        max_year = end_use[nm.Fields.harvest_year].max()
        copy_frame = end_use[end_use[nm.Fields.harvest_year] == max_year].copy(deep=True)
        copy_frame[nm.Fields.harvest_year] = max_year + 1
        copy_frame[nm.Fields.ccf] = 0
        copy_frame[nm.Fields.timber_product_results] = 0
        copy_frame[nm.Fields.primary_product_results] = 0
        copy_frame[nm.Fields.end_use_results] = 0

        end_use = end_use.append(copy_frame)

        self.results.end_use_products = end_use
        self.results.working_table = end_use

        return

    def calculate_products_in_use(self):
        """Calculate the amount of end use products from each vintage year that are still in use
        during each inventory year.
        """
        end_use = self.results.working_table
        # Make sure the rows are ascending to do the half life. Don't do this inplace
        end_use = end_use.sort_values(by=nm.Fields.harvest_year)
        end_use = end_use.merge(self.end_use_products, how='outer', on=[nm.Fields.primary_product_id, nm.Fields.end_use_id])
        
        end_use[nm.Fields.end_use_sum] = end_use.groupby(by=nm.Fields.end_use_id)[nm.Fields.end_use_results].cumsum()

        # def halflife_func(q: mp.Queue, df: pd.DataFrame) -> pd.DataFrame:
        def halflife_func(df: pd.DataFrame) -> pd.DataFrame:
            halflife = df[nm.Fields.end_use_halflife].iloc[0]
            
            if halflife == 0:
                df.loc[:, nm.Fields.products_in_use] = df[nm.Fields.end_use_results]
            else:
                weightspace = [math.exp(-math.log(2) * x / halflife) for x in range(len(df))]    
                for h in range(len(df)):
                    v = df[nm.Fields.end_use_results].iloc[h]
                    weights = weightspace[:len(df) - h]
                    decayed = [v * w * self.end_use_loss_factor for w in weights]
                    df.iloc[h:, df.columns.get_loc(nm.Fields.products_in_use)] = df.iloc[h:, df.columns.get_loc(nm.Fields.products_in_use)] + decayed
            
            return df
        
        end_use[nm.Fields.products_in_use] = 0
        
        s = timeit.default_timer()
        # x = None
        # with mp.Pool() as pool:
        #     x = pool.map(halflife_func, end_use.groupby(by=nm.Fields.end_use_id))
        # products_in_use = reduce(lambda x, y: pd.concat(x, y), x)
        
        products_in_use = end_use.groupby(by=nm.Fields.end_use_id).apply(halflife_func)
        print('PRODUCTS IN USE APPLY', timeit.default_timer() - s)
        # s = timeit.default_timer()
        # products_in_use = end_use.groupby(by=nm.Fields.end_use_id).parallel_apply(halflife_func)
        # print('PARALLEL', timeit.default_timer() - s)
        
        # TODO try to get dask tpo speed this up
        # end_use = dd.from_pandas(end_use, npartitions=30)
        # products_in_use = end_use.map_partitions(lambda df: df.groupby(by=nm.Fields.end_use_id).apply((lambda dg: halflife_func(*dg)), axis=1)).compute(get=get)
        
        self.results.products_in_use = products_in_use
        self.results.working_table = products_in_use

        return

    def calculate_discarded_dispositions(self):
        """Calculate the amount discarded during each inventory year and divide it up between the
        different dispositions (landfills, dumps, etc).
        """

        # Calculate the amount of each end use from year y that was discarded in year i 
        # by subtracting the products in use from the amount of harvested product and
        # then subtracting the amount discarded in previous years.
        products_in_use = self.results.working_table
        products_in_use[nm.Fields.discarded_products_results] = products_in_use[nm.Fields.end_use_sum] - products_in_use[nm.Fields.products_in_use] 
        
        # Tease out the NEW discarded amounts for this year to dispose of them in the correct pools
        adjust = products_in_use.groupby(by=nm.Fields.end_use_id)[nm.Fields.discarded_products_results].shift()
        products_in_use[nm.Fields.discarded_in_year] = products_in_use[nm.Fields.discarded_products_results] - adjust
    
        # Zero out the stuff that was fuel.
        df_filter = products_in_use[nm.Fields.fuel] == 1
        # products_in_use.loc[df_filter, nm.Fields.discarded_products_adjusted] = 0
        products_in_use.loc[df_filter, nm.Fields.discarded_products_results] = 0

        # Multiply the amount discarded this year by the disposition ratios to get the
        # amount that goes into landfills, dumps, etc, and then add these to the 
        # discarded disposition totals for stuff discarded in year i.
        products_in_use = products_in_use.merge(self.discarded_disposition_ratios, how='outer', on=[nm.Fields.harvest_year, nm.Fields.discard_type_id])
        
        # If the years mismatch, there will be NaN, so get rid of them
        products_in_use = products_in_use.dropna()

        products_in_use[nm.Fields.discard_dispositions] = products_in_use[nm.Fields.discarded_in_year] * products_in_use[nm.Fields.discard_destination_ratio]
        # products_in_use[nm.Fields.discard_dispositions] = products_in_use.groupby(by=[nm.Fields.end_use_id, nm.Fields.discard_type_id, nm.Fields.discard_destination_id])[nm.Fields.discard_dispositions_in_year].cumsum()

        # Drop the lowest year to prevent negative number creep
        # products_in_use = products_in_use[products_in_use[nm.Fields.harvest_year] != products_in_use[nm.Fields.harvest_year].min()]
        
        self.results.discarded_products = products_in_use
        self.results.working_table = products_in_use
        
        return

    def calculate_dispositions(self):
        """Calculate the amounts of discarded products that have been emitted, are still remaining, 
        etc., for each inventory year.
        """

        # Calculate the amount in landfills that was discarded during this inventory year
        # that is subject to decay by multiplying the amount in the landfill by the
        # landfill-fixed-ratio. This will be used in later iterations of the i loop.
        destinations = self.md.data[nm.Tables.discard_destinations]
        landfill_id = destinations[destinations[nm.Fields.discard_description] == nm.Fields.landfills][nm.Fields.discard_destination_id].iloc[0]

        discard_types = self.md.discard_types_dict

        # Calculate the amount in landfills that was discarded during this inventory year
        # that is subject to decay by multiplying the amount in the landfill by the
        # landfill-fixed-ratio. This will be used in later iterations of the i loop.
        dispositions = self.results.working_table 
        dispositions[nm.Fields.can_decay] = 0
        df_filter = (dispositions[nm.Fields.discard_destination_id] == landfill_id) & (dispositions[nm.Fields.discard_type_id] == self.md.paper_val)
        dispositions.loc[df_filter, nm.Fields.can_decay] = dispositions.loc[df_filter, nm.Fields.discard_dispositions] * (1 - discard_types[nm.Fields.paper][nm.Fields.landfill_fixed_ratio])
        df_filter = (dispositions[nm.Fields.discard_destination_id] == landfill_id) & (dispositions[nm.Fields.discard_type_id] == self.md.wood_val)
        dispositions.loc[df_filter, nm.Fields.can_decay] = dispositions.loc[df_filter, nm.Fields.discard_dispositions] * (1 - discard_types[nm.Fields.wood][nm.Fields.landfill_fixed_ratio])

        # set the decay ratios
        diposition_halflifes = self.md.disposition_to_halflife
        df_filter = (dispositions[nm.Fields.discard_type_id] == self.md.paper_val)
        dispositions.loc[df_filter, nm.Fields.decay_ratio] = dispositions.loc[df_filter, nm.Fields.discard_destination_id].map(diposition_halflifes[nm.Fields.paper])
        df_filter = (dispositions[nm.Fields.discard_type_id] == self.md.wood_val)
        dispositions.loc[df_filter, nm.Fields.decay_ratio] = dispositions.loc[df_filter, nm.Fields.discard_destination_id].map(diposition_halflifes[nm.Fields.wood])


        # Get the amounts discarded in year y that are subject to decay.
        df_filter = (dispositions[nm.Fields.discard_destination_id] == landfill_id)
        dispositions.loc[~df_filter, nm.Fields.can_decay] = dispositions.loc[~df_filter, nm.Fields.discard_dispositions]

        # Calculate the amounts that were discarded in year y that could decay but
        # are still remaining in year i, by plugging the amount subject to decay into
        # the decay formula that uses half lives.

        def halflife_func(df):
            halflife = df[nm.Fields.decay_ratio].iloc[0]

            if halflife == 0:
                df.loc[:, nm.Fields.discard_remaining] = 0
            else:  
                weightspace = [math.exp(-math.log(2) * x / halflife) for x in range(len(df))]    
                for h in range(len(df)):
                    v = df[nm.Fields.can_decay].iloc[h]
                    weights = weightspace[:len(df) - h]
                    decayed = [v * w for w in weights]
                    df.iloc[h:, df.columns.get_loc(nm.Fields.discard_remaining)] = df.iloc[h:, df.columns.get_loc(nm.Fields.discard_remaining)] + decayed            
            return df
        
        df_key = [nm.Fields.end_use_id, nm.Fields.discard_type_id, nm.Fields.discard_destination_id]
        dispositions[nm.Fields.discard_remaining] = 0

        s = timeit.default_timer()
        dispositions = dispositions.groupby(by=df_key).apply(halflife_func)
        print('DISPOSITIONS APPLY', timeit.default_timer() - s)

        dispositions['could_decay'] = dispositions.groupby(by=df_key)[nm.Fields.can_decay].cumsum()

        # Calculate emissions from stuff discarded in year y by subracting the amount
        # remaining from the total amount that could decay.
        dispositions[nm.Fields.emitted] = dispositions['could_decay'] - dispositions[nm.Fields.discard_remaining]
        dispositions[nm.Fields.present] = dispositions[nm.Fields.discard_remaining]

        # Landfills are a bit different. Not all of it is subject to decay, so get the fixed amount and add it to present through time
        # Something like discard_dispositions - can_decay -> cumsum
        df_filter = (dispositions[nm.Fields.discard_destination_id] == landfill_id) & (dispositions[nm.Fields.discard_type_id] == self.md.paper_val)
        dispositions.loc[df_filter, nm.Fields.present] = dispositions.loc[df_filter, nm.Fields.discard_dispositions] - dispositions.loc[df_filter, nm.Fields.can_decay]
        dispositions.loc[df_filter, nm.Fields.present] = dispositions.loc[df_filter].groupby(by=df_key).agg({nm.Fields.present: np.cumsum})

        df_filter = (dispositions[nm.Fields.discard_destination_id] == landfill_id) & (dispositions[nm.Fields.discard_type_id] == self.md.wood_val)
        dispositions.loc[df_filter, nm.Fields.present] = dispositions.loc[df_filter, nm.Fields.discard_dispositions] - dispositions.loc[df_filter, nm.Fields.can_decay]
        dispositions.loc[df_filter, nm.Fields.present] = dispositions.loc[df_filter].groupby(by=df_key).agg({nm.Fields.present: np.cumsum})

        self.results.dispositions = dispositions
        self.results.working_table = dispositions

        return

    def calculate_fuel_burned(self):
        """Calculate the amount of fuel burned during each vintage year.
        """
        dispositions = self.results.working_table

        # Loop through all of the primary products that are fuel and add the amounts of that
        # product to the total for this year.
        df_keys = [nm.Fields.harvest_year, nm.Fields.primary_product_id, nm.Fields.primary_product_results]
        fuel_captured = dispositions.loc[dispositions[nm.Fields.fuel] == 1, df_keys].drop_duplicates()

        self.results.burned_captured = fuel_captured

        return

    def calculate_discarded_burned(self):
        """Calculate the amount of discarded products that were burned.
        """
        # For each year, sum up the amount of discarded paper and wood that are burned, and then
        # multiply that by the burned-with-energy-capture ratio for that year.

        dispositions = self.results.working_table
        dispositions_not_fuel = dispositions[dispositions[nm.Fields.fuel] == 0]

        discard_destinations = self.md.data[nm.Tables.discard_destinations]
        burned = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.burned][nm.Fields.discard_destination_id].iloc[0]

        burned_not_captured = dispositions_not_fuel[dispositions_not_fuel[nm.Fields.discard_destination_id] == burned]
        # burned_not_captured = burned_not_captured[[nm.Fields.harvest_year, ]]


        # TODO finish this function
        # Burned dispositions only? Is this NOT FUEL only?

        return

    def summarize(self):

        results = self.results.working_table
        conversion = self.md.data[nm.Tables.ccf_c_conversion][[nm.Fields.primary_product_id, nm.Fields.conversion_factor]]

        results = results.merge(conversion, on=nm.Fields.primary_product_id)

        C = nm.Fields.c

        results[C(nm.Fields.products_in_use)] = results[nm.Fields.products_in_use] * results[nm.Fields.conversion_factor]
        results[C(nm.Fields.present)] = results[nm.Fields.present] * results[nm.Fields.conversion_factor]
        results[C(nm.Fields.emitted)] = results[nm.Fields.emitted] * results[nm.Fields.conversion_factor]

        df_keys = [nm.Fields.harvest_year, C(nm.Fields.products_in_use)]
        products_in_use = results.loc[:, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.products_in_use): np.sum})
        self.results.products_in_use = products_in_use
        
        # Get discard destination IDs for sorting through results
        discard_destinations = self.md.data[nm.Tables.discard_destinations]

        burned_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.burned][nm.Fields.discard_destination_id].iloc[0]
        df_keys = [nm.Fields.harvest_year, C(nm.Fields.emitted)]
        burned = results.loc[results[nm.Fields.discard_destination_id] == burned_id, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.emitted): np.sum})
        self.results.burned = burned

        composted_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.composted][nm.Fields.discard_destination_id].iloc[0]
        composted = results.loc[results[nm.Fields.discard_destination_id] == composted_id, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.emitted): np.sum})
        self.results.composted = composted

        df_keys = [nm.Fields.harvest_year, C(nm.Fields.present)]
        recycled_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.recycled][nm.Fields.discard_destination_id].iloc[0]
        recovered_in_use = results.loc[results[nm.Fields.discard_destination_id] == recycled_id, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.present): np.sum})
        self.results.recovered_in_use = recovered_in_use

        landfill_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.landfills][nm.Fields.discard_destination_id].iloc[0]
        in_landfills = results.loc[results[nm.Fields.discard_destination_id] == landfill_id, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.present): np.sum})
        self.results.in_landfills  = in_landfills

        dump_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.dumps][nm.Fields.discard_destination_id].iloc[0]
        in_dumps = results.loc[results[nm.Fields.discard_destination_id] == dump_id, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.present): np.sum})
        self.results.in_dumps = in_dumps

        fuelwood = self.results.burned_captured.merge(conversion, on=nm.Fields.primary_product_id)
        fuelwood[C(nm.Fields.primary_product_results)] = fuelwood[nm.Fields.primary_product_results] * fuelwood[nm.Fields.conversion_factor]
        fuelwood = fuelwood.groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.primary_product_results): np.sum})
        fuelwood[C(nm.Fields.burned_with_energy_capture)] = fuelwood.sort_values(by=nm.Fields.harvest_year).drop_duplicates().agg({C(nm.Fields.primary_product_results): np.cumsum})
        self.results.fuelwood = fuelwood

        df_keys = [nm.Fields.harvest_year, C(nm.Fields.emitted)]
        landfills_emitted = results.loc[results[nm.Fields.discard_destination_id] == landfill_id, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.emitted): np.sum})
        dumps_emitted = results.loc[results[nm.Fields.discard_destination_id] == dump_id, df_keys].groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.emitted): np.sum})
        recycled_emitted = results.loc[results[nm.Fields.discard_destination_id] == recycled_id, df_keys].drop_duplicates().groupby(by=nm.Fields.harvest_year).agg({C(nm.Fields.emitted): np.sum})
        burned_emitted = burned
        compost_emitted = composted

        self.results.emissions = {'fuelwood': fuelwood, 'landfills_emitted': landfills_emitted, 'dumps_emitted': dumps_emitted, 'recycled_emitted': recycled_emitted, 'burned_emitted': burned_emitted, 'compost_emitted': compost_emitted}

        recovered_in_use = recovered_in_use.rename(columns={C(nm.Fields.present): C('recovered')})
        all_in_use = products_in_use.merge(recovered_in_use, how='inner', on=nm.Fields.harvest_year).drop_duplicates()
        in_landfills = in_landfills.rename(columns={C(nm.Fields.present): 'landfills_' + C(nm.Fields.present)})
        all_in_use = all_in_use.merge(in_landfills, how='inner', on=nm.Fields.harvest_year).drop_duplicates()
        in_dumps = in_dumps.rename(columns={C(nm.Fields.present): 'dumps_' + C(nm.Fields.present)})
        all_in_use = all_in_use.merge(in_dumps, how='inner', on=nm.Fields.harvest_year).drop_duplicates()
        all_in_use[C(nm.Fields.swds)] = all_in_use.drop(columns=[C(nm.Fields.products_in_use)]).sum(axis=1)
        self.results.all_in_use = all_in_use
        
        self.results.working_table = results

        # Select the unique combination of year, timber product, primary product, and convert primary products
        # to carbon for analysis of results
        df_keys = [nm.Fields.harvest_year, nm.Fields.timber_product_id, nm.Fields.primary_product_id]
        df_values = [nm.Fields.primary_product_results, nm.Fields.conversion_factor]
        timber_products_conversion = results[df_keys + df_values].drop_duplicates()
        timber_products_conversion[C(nm.Fields.primary_product_results)] = timber_products_conversion[nm.Fields.primary_product_results] * timber_products_conversion[nm.Fields.conversion_factor]
        timber_products_agg = timber_products_conversion.groupby(by=[nm.Fields.harvest_year])[C(nm.Fields.primary_product_results)].sum()
        timber_products_agg = pd.DataFrame(timber_products_agg)
        timber_products_agg = timber_products_agg.merge(self.harvests, on=nm.Fields.harvest_year)
        self.results.annual_timber_products = timber_products_agg

        return

    def convert_c02_e(self):

        C = nm.Fields.c
        CO2 = nm.Fields.co2

        emissions = self.results.emissions
        emissions['fuelwood'][CO2(nm.Fields.burned_with_energy_capture)] = emissions['fuelwood'][C(nm.Fields.burned_with_energy_capture)].apply(self.c_to_co2d)
        emissions['landfills_emitted'][CO2(nm.Fields.landfills)] = emissions['landfills_emitted'][C(nm.Fields.emitted)].apply(self.c_to_co2d)
        emissions['dumps_emitted'][CO2(nm.Fields.dumps)] = emissions['dumps_emitted'][C(nm.Fields.emitted)].apply(self.c_to_co2d)
        emissions['recycled_emitted'][CO2(nm.Fields.recycled)] = emissions['recycled_emitted'][C(nm.Fields.emitted)].apply(self.c_to_co2d)
        emissions['burned_emitted'][CO2(nm.Fields.emitted)] = emissions['burned_emitted'][C(nm.Fields.emitted)].apply(self.c_to_co2d)
        emissions['compost_emitted'][CO2(nm.Fields.composted)] = emissions['compost_emitted'][C(nm.Fields.emitted)].apply(self.c_to_co2d)

        self.results.emissions = emissions

        total_all_dispositions = self.results.all_in_use
        emissions['fuelwood'] = emissions['fuelwood'][CO2(nm.Fields.burned_with_energy_capture)]
        total_all_dispositions = total_all_dispositions.merge(emissions['fuelwood'], on=nm.Fields.harvest_year)    
        emissions['landfills_emitted'] = emissions['landfills_emitted'][CO2(nm.Fields.landfills)]
        total_all_dispositions = total_all_dispositions.merge(emissions['landfills_emitted'], on=nm.Fields.harvest_year)
        emissions['dumps_emitted'] = emissions['dumps_emitted'][CO2(nm.Fields.dumps)]
        total_all_dispositions = total_all_dispositions.merge(emissions['dumps_emitted'], on=nm.Fields.harvest_year)
        emissions['recycled_emitted'] = emissions['recycled_emitted'][CO2(nm.Fields.recycled)]
        total_all_dispositions = total_all_dispositions.merge(emissions['recycled_emitted'], on=nm.Fields.harvest_year)
        emissions['burned_emitted'] = emissions['burned_emitted'][CO2(nm.Fields.emitted)]
        emissions['burned_emitted'] = emissions['burned_emitted'].rename(CO2(nm.Fields.burned_wo_energy_capture))
        total_all_dispositions = total_all_dispositions.merge(emissions['burned_emitted'], on=nm.Fields.harvest_year)
        emissions['compost_emitted'] = emissions['compost_emitted'][CO2(nm.Fields.composted)]
        total_all_dispositions = total_all_dispositions.merge(emissions['compost_emitted'], on=nm.Fields.harvest_year)

        mtc_columns = [x for x in total_all_dispositions.columns if x.find('mtc') > 1]
        co2e_columns = [x for x in total_all_dispositions.columns if x.find('co2e') > 1]

        mtc_rename = [x.replace('mtc', 'co2e') for x in mtc_columns]
        total_all_dispositions[mtc_rename] = total_all_dispositions[mtc_columns].apply(self.c_to_co2d, axis = 1)
        total_all_dispositions[CO2(nm.Fields.emitted)] = total_all_dispositions[co2e_columns].sum(axis=1)

        total_all_dispositions = total_all_dispositions.merge(self.results.annual_timber_products, on=nm.Fields.harvest_year)
        total_all_dispositions[C(nm.Fields.primary_product_sum)] = total_all_dispositions[C(nm.Fields.primary_product_results)].cumsum()
        total_all_dispositions[CO2(nm.Fields.primary_product_sum)] = total_all_dispositions[C(nm.Fields.primary_product_sum)].apply(self.c_to_co2d)

        df_keys = [nm.Fields.harvest_year, CO2(nm.Fields.primary_product_sum), CO2(nm.Fields.products_in_use), CO2(nm.Fields.swds), CO2(nm.Fields.emitted)]
        big_table = total_all_dispositions[df_keys].drop_duplicates()
        big_table[nm.Fields.accounted] = big_table[df_keys[2:]].sum(axis = 1)
        big_table[nm.Fields.error] = big_table[CO2(nm.Fields.primary_product_sum)] - big_table[nm.Fields.accounted]

        self.results.big_table = big_table
        self.results.total_all_dispositions = total_all_dispositions

        return

    def final_table(self):
        
        final = self.results.fuelwood.merge(self.results.burned, on=nm.Fields.harvest_year).merge(self.results.all_in_use, on=nm.Fields.harvest_year)

        C = nm.Fields.c
        CO2 = nm.Fields.co2
        CHANGE = nm.Fields.change

        final[C(nm.Fields.products_in_use)] = final[C(nm.Fields.products_in_use)].cumsum()

        final[CHANGE(CO2(nm.Fields.burned_with_energy_capture))] = final[CO2(nm.Fields.burned_with_energy_capture)].diff()
        final[CHANGE(CO2(nm.Fields.emitted))] = final[CO2(nm.Fields.emitted)].diff()
        final[CHANGE(C(nm.Fields.products_in_use))] = final[C(nm.Fields.products_in_use)].diff()
        final[CHANGE(C(nm.Fields.swds))] = final[C(nm.Fields.swds)].diff()

        self.results.final = final

        self.results.big_table.to_csv('x_big_table.csv')
        self.results.total_all_dispositions.to_csv('x_total_all.csv')
        self.results.working_table.to_csv('x_working.csv')
        self.results.final.to_csv('x_final.csv')

        return

    def c_to_co2d(self, c: float) -> float:
        """Convert C to CO2e.

        Args:
            c (float): the C value to convert

        Returns:
            float: Units of CO2 
        """
        return c * 44.0 / 12.0

    def print_debug_df(self, df):
        """Print the head and tail of a DataFrame to console. Useful for testing

        Args:
            df (DataFrame): A DataFrame of interest to print
        """
        print(df.head(10))
        print(df.tail(10))

    def print_debug_df_2(self, df):
        df = df[df[nm.Fields.end_use_id] == 212]
        self.print_debug_df(df)

    def memory_usage(self, df):
        dfm = df.memory_usage()
        dfm = dfm / 1024 / 1024
        print('\n', dfm, '\n')

    def memory_usage_total(self, df):
        dfs = df.memory_usage().sum()
        dfs = dfs / 1024 / 1024
        print('{} MB used'.format(dfs))

    def save(self, df):
        df.to_csv('temp.csv')

    def save_2(self, df):
        df = df[df[nm.Fields.end_use_id] == 212]
        df.to_csv('temp.csv')
    