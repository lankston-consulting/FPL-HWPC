import numpy as np
import pandas as pd

from hwpc import model_data
from hwpc import results
from hwpc.names import Names as nm


class Model(object):

    def __init__(self) -> None:
        super().__init__()

        self.md = model_data.ModelData()

        self.harvests = self.md.data[nm.Tables.harvest]

        self.timber_product_ratios = self.md.data[nm.Tables.timber_products_data]
        self.primary_product_ratios = self.md.data[nm.Tables.primary_product_ratios]
        
        self.end_use_ratios = self.md.data[nm.Tables.end_use_ratios]
        self.end_use_products = self.md.data[nm.Tables.end_use_products]
        
        self.discarded_disposition_ratios = self.md.data[nm.Tables.discard_disposition_ratios]

        # number of years in model
        self.years = self.md.get_harvest_years()
        self.num_years = len(self.years)

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

        self.results.save_results()
        self.results.save_total_dispositions()
        #self.results.save_fuel_captured()
        #self.results.save_end_use_products()
        #self.results.save_discarded_wood_or_paper()

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

        end_use_halflives = self.end_use_products[[nm.Fields.end_use_id, nm.Fields.end_use_halflife]]
        
        def halflife_func(df):
            id = df[nm.Fields.end_use_id].iloc[0]
            halflife = end_use_halflives[end_use_halflives[nm.Fields.end_use_id] == id]
            halflife = halflife[nm.Fields.end_use_halflife].iloc[0]

            if halflife == 0:
                df.loc[:, nm.Fields.products_in_use] = df[nm.Fields.end_use_results]
            else:  
                df.loc[:, nm.Fields.products_in_use] = df[nm.Fields.end_use_results].ewm(halflife=halflife).mean() * self.end_use_loss_factor
            
            return df
            
        products_in_use = end_use.groupby(by=nm.Fields.end_use_id).apply(halflife_func)
        
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
        products_in_use[nm.Fields.discarded_products_results] = products_in_use[nm.Fields.end_use_results] - products_in_use[nm.Fields.products_in_use] 
        products_in_use[nm.Fields.running_discarded_products] = products_in_use.groupby(by=nm.Fields.end_use_id).agg({nm.Fields.discarded_products_results: np.cumsum})
        
        products_in_use[nm.Fields.discarded_products_adjustment] = products_in_use[nm.Fields.end_use_results] - products_in_use[nm.Fields.running_discarded_products]
        products_in_use[nm.Fields.discarded_products_adjusted] = products_in_use[nm.Fields.discarded_products_results] - products_in_use[nm.Fields.discarded_products_adjustment]

        # Merge in the end_use_products table to get the Fuel binary flag and the Paper binary flag
        discarded_products = products_in_use.merge(self.end_use_products, how='outer', on=[nm.Fields.primary_product_id, nm.Fields.end_use_id])

        # Zero out the stuff that was fuel.
        df_filter = discarded_products[nm.Fields.fuel] == 1
        discarded_products.loc[df_filter, nm.Fields.discarded_products_adjusted] = 0

        # Calculate the amount of wood and paper from year y discarded in year i by 
        # summing all discards up, summing all paper discards up, and then subtracting
        # the paper total from the grand total to get the amount of wood.
        self.results.discarded_wood_paper = discarded_products.groupby(by=[nm.Fields.harvest_year, nm.Fields.discard_type_id]).agg({nm.Fields.discarded_products_adjusted: np.sum})
        self.results.discarded_wood_paper = self.results.discarded_wood_paper.rename(columns={nm.Fields.discarded_products_adjusted: nm.Fields.discarded_products_type_sum})

        # Multiply the amount discarded this year by the disposition ratios to get the
        # amount that goes into landfills, dumps, etc, and then add these to the 
        # discarded disposition totals for stuff discarded in year i.
        discarded_products = discarded_products.merge(self.results.discarded_wood_paper , how='outer', on=[nm.Fields.harvest_year, nm.Fields.discard_type_id])
        discarded_products = discarded_products.merge(self.discarded_disposition_ratios, how='outer', on=[nm.Fields.harvest_year, nm.Fields.discard_type_id])
        # If the years mismatch, there will be NaN, so get rid of them
        discarded_products = discarded_products.dropna()

        discarded_products[nm.Fields.discard_dispositions] = discarded_products[nm.Fields.discarded_products_type_sum] * discarded_products[nm.Fields.discard_destination_ratio]
        self.results.discarded_products = discarded_products

        self.results.working_table = discarded_products
        
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
        dump_id = destinations[destinations[nm.Fields.discard_description] == nm.Fields.dumps][nm.Fields.discard_destination_id].iloc[0]
        recycle_id = destinations[destinations[nm.Fields.discard_description] == nm.Fields.recycled][nm.Fields.discard_destination_id].iloc[0]

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
                df.loc[:, nm.Fields.discard_remaining] = df[nm.Fields.can_decay].ewm(halflife=halflife).mean() 
            
            return df
        
        df_key = [nm.Fields.timber_product_id, nm.Fields.end_use_id, nm.Fields.primary_product_id, nm.Fields.discard_type_id, nm.Fields.discard_destination_id]
        dispositions = dispositions.groupby(by=df_key).apply(halflife_func)

        # Calculate emissions from stuff discarded in year y by subracting the amount
        # remaining from the total amount that could decay.
        dispositions[nm.Fields.emitted] = dispositions[nm.Fields.can_decay] - dispositions[nm.Fields.discard_remaining]
        # Add this year's emissions to the total for the current inventory year.
        dispositions[nm.Fields.emitted_sum] = dispositions.groupby(by=df_key).agg({nm.Fields.emitted: np.cumsum})

        dispositions[nm.Fields.present] = dispositions.groupby(by=df_key).agg({nm.Fields.discard_remaining: np.cumsum})

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
        
        # max_year = dispositions[nm.Fields.harvest_year].max()
        # total_dispositions = dispositions.loc[dispositions[nm.Fields.harvest_year] == max_year, df_key + [nm.Fields.harvest_year, nm.Fields.discard_remaining]]

        # self.results.total_dispositions =  total_dispositions

        return

    def calculate_fuel_burned(self):
        """Calculate the amount of fuel burned during each vintage year.
        """
        dispositions = self.results.working_table

        # Loop through all of the primary products that are fuel and add the amounts of that
        # product to the total for this year.
        df_keys = [nm.Fields.harvest_year, nm.Fields.primary_product_id, nm.Fields.primary_product_results]
        fuel_captured = dispositions.loc[dispositions[nm.Fields.fuel] == 1, df_keys].drop_duplicates()
        fuel_captured = fuel_captured.groupby(by=nm.Fields.harvest_year).agg({nm.Fields.primary_product_results: np.sum})
        fuel_captured[nm.Fields.burned_with_energy_capture] = fuel_captured.sort_values(by=nm.Fields.harvest_year).agg({nm.Fields.primary_product_results: np.cumsum})

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
        
        discard_destinations = self.md.data[nm.Tables.discard_destinations]

        burned_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.burned][nm.Fields.discard_destination_id].iloc[0]
        df_keys = [nm.Fields.harvest_year, nm.Fields.emitted_sum]
        burned = results.loc[results[nm.Fields.discard_destination_id] == burned_id, df_keys].drop_duplicates()

        composted_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.composted][nm.Fields.discard_destination_id].iloc[0]
        composted = results.loc[results[nm.Fields.discard_destination_id] == composted_id, df_keys].drop_duplicates()

        products_in_use = self.results.products_in_use.groupby(by=[nm.Fields.harvest_year]).agg({nm.Fields.products_in_use: np.sum})

        df_keys = [nm.Fields.harvest_year, nm.Fields.present]
        recycled_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.recycled][nm.Fields.discard_destination_id].iloc[0]
        recovered_in_use = results.loc[results[nm.Fields.discard_destination_id] == recycled_id, df_keys].drop_duplicates()

        landfill_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.landfills][nm.Fields.discard_destination_id].iloc[0]
        in_landfills = results.loc[results[nm.Fields.discard_destination_id] == landfill_id, df_keys].drop_duplicates()

        dump_id = discard_destinations[discard_destinations[nm.Fields.discard_description] == nm.Fields.dumps][nm.Fields.discard_destination_id].iloc[0]
        in_dumps = results.loc[results[nm.Fields.discard_destination_id] == dump_id, df_keys].drop_duplicates()

        fuelwood = self.results.burned_captured

        df_keys = [nm.Fields.harvest_year, nm.Fields.emitted_sum]
        landfills_emitted = results.loc[results[nm.Fields.discard_destination_id] == landfill_id, df_keys].drop_duplicates()
        dumps_emitted = results.loc[results[nm.Fields.discard_destination_id] == dump_id, df_keys].drop_duplicates()
        recycled_emitted = results.loc[results[nm.Fields.discard_destination_id] == recycled_id, df_keys].drop_duplicates()
        burned_emitted = burned
        compost_emitted = composted

        all_in_use = products_in_use.merge(recovered_in_use, how='inner', on=nm.Fields.harvest_year)

        results[nm.Fields.carbon] = results[nm.Fields.discard_remaining] * results[nm.Fields.conversion_factor]
        results[nm.Fields.co2] = results[nm.Fields.carbon].apply(self.c_to_co2d)

        self.results.working_table = results
        return

    def convert_emissions_c02_e(self):
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
    