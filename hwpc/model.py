import numpy as np
import pandas as pd

from hwpc import model_data
from hwpc import results
from hwpc.names import Names as nm


class Model(object):

    def __init__(self) -> None:
        super().__init__()

        self.md = model_data.ModelData()

        self.region = self.md.get_region_id('West')

        self.harvests = self.md.data[nm.Tables.harvest]

        self.timber_product_ratios = self.md.data[nm.Tables.timber_products]
        self.primary_product_ratios = self.md.data[nm.Tables.primary_product_ratios]

        # TODO add switch for loading user supplied primary product data instead
        # for now use a default region and limit the default table
        self.primary_product_ratios = self.primary_product_ratios[self.primary_product_ratios[nm.Fields.region_id] == self.region]
        
        self.end_use_ratios = self.md.data[nm.Tables.end_use_ratios]
        self.end_use_halflifes = self.md.data[nm.Tables.end_use_halflifes]
        
        self.discarded_disposition_ratios = self.md.data[nm.Tables.discard_disposition_ratios]

        # number of years in model
        self.years = self.md.get_harvest_years()
        self.num_years = len(self.years)

        # the amount of product that is not lost
        self.end_use_loss_factor = 0.92

        # default percent of product that is burned with energy capture
        self.default_burned_energy_capture = 0

        self.results = results.Results()

    def run(self, region='West', iterations=1):
        
        self.calculate_primary_product_mcg()
        self.calculate_end_use_products()
        self.calculate_products_in_use()
        self.calculate_discarded_dispositions()

        return

    def calculate_primary_product_mcg(self):
        """Calculate the amounts of primary products (MgC) harvested in each year.
        """

        # Calculate timber products (CCF) by multiplying the harvest-to-timber ratio for each
        # timber product by the amount harvested that year.

        timber_products_ccf = self.timber_product_ratios.merge(self.harvests, how='outer')
        timber_products_ccf = timber_products_ccf.rename(columns={nm.Fields.ratio: nm.Fields.timber_product_ratio})
        timber_products_ccf[nm.Fields.timber_product_results] = timber_products_ccf[nm.Fields.timber_product_ratio] * timber_products_ccf[nm.Fields.ccf]

        timber_products_ccf = timber_products_ccf.dropna()

        # Calculate primary products (CCF) by multiplying the timber-to-primary ratio for each 
        # primary product by the amount of the corresponding timber product. Then convert to MgC
        # by multiplying by the CCF-to-MgC ratio for that primary product.
        
        # Append the timber product id to the primary product table
        primary_products_ccf = self.primary_product_ratios
        primary_products_ccf = primary_products_ccf.rename(columns={nm.Fields.ratio: nm.Fields.primary_product_ratio})
        primary_products_ccf[nm.Fields.timber_product_id] = primary_products_ccf[nm.Fields.primary_product_id].map(self.md.primary_product_to_timber_product)
        
        primary_products_ccf = primary_products_ccf.merge(timber_products_ccf, how='outer', on=[nm.Fields.harvest_year, nm.Fields.timber_product_id])
        primary_products_ccf[nm.Fields.primary_product_results] = primary_products_ccf[nm.Fields.primary_product_ratio] * primary_products_ccf[nm.Fields.ccf]

        primary_products_ccf = primary_products_ccf.dropna()

        # TODO convert mgc I guess?        

        self.results.timber_products_ccf = timber_products_ccf
        self.results.primary_products_ccf = primary_products_ccf

        return

    def calculate_end_use_products(self):
        """Calculate the amount of end use products harvested in each year.
        """

        # Multiply the primary-to-end-use ratio for each end use product by the amount of the
        # corresponding primary product.

        end_use = self.end_use_ratios
        end_use = end_use.rename(columns={nm.Fields.ratio: nm.Fields.end_use_ratio})
        end_use[nm.Fields.primary_product_id] = end_use[nm.Fields.end_use_id].map(self.md.end_use_to_primary_product)

        end_use = end_use.merge(self.results.primary_products_ccf, how='outer', on=[nm.Fields.harvest_year, nm.Fields.primary_product_id])
        end_use[nm.Fields.end_use_results] = end_use[nm.Fields.end_use_ratio] * end_use[nm.Fields.primary_product_results]

        end_use = end_use.dropna()

        self.results.end_use_ccf = end_use

        return

    def calculate_products_in_use(self):
        """Calculate the amount of end use products from each vintage year that are still in use
        during each inventory year.
        """
        end_use_ccf = self.results.end_use_ccf
        # Make sure the rows are ascending to do the half life. Don't do this inplace
        end_use_ccf = end_use_ccf.sort_values(by=nm.Fields.harvest_year)

        end_use_halflives = self.end_use_halflifes[[nm.Fields.end_use_id, nm.Fields.end_use_halflife]]
        
        def halflife_func(df):
            id = df[nm.Fields.end_use_id].iloc[0]
            halflife = end_use_halflives[end_use_halflives[nm.Fields.end_use_id] == id]
            halflife = halflife[nm.Fields.end_use_halflife].iloc[0]

            if halflife == 0:
                df.loc[:, nm.Fields.end_use_in_use] = df[nm.Fields.end_use_results]
            else:  
                df.loc[:, nm.Fields.end_use_in_use] = df[nm.Fields.end_use_results].ewm(halflife=halflife).mean() * self.end_use_loss_factor
            
            return df
            
        products_in_use = end_use_ccf.groupby(by=nm.Fields.end_use_id).apply(halflife_func)

        self.results.products_in_use = products_in_use

        return

    def calculate_discarded_dispositions(self):
        """Calculate the amount discarded during each inventory year and divide it up between the
        different dispositions (landfills, dumps, etc).
        """

        products_in_use = self.results.products_in_use
        
        discarded_disposition_ratios = self.discarded_disposition_ratios
        discarded_disposition_ratios = discarded_disposition_ratios.rename(columns={nm.Fields.ratio: nm.Fields.discard_destination_ratio})
        discarded_disposition_ratios = discarded_disposition_ratios.sort_values(by=[nm.Fields.discard_type_id, nm.Fields.discard_destination_id, nm.Fields.harvest_year])

        # for id in ids:
        #     end_use_by_id = products_in_use[products_in_use[nm.Fields.end_use_id] == id]
        #     discarded_disposition_ratios

        discarded_products = products_in_use.merge(discarded_disposition_ratios, how='outer', on=nm.Fields.harvest_year)
        discarded_products = discarded_products.dropna()
        discarded_products[nm.Fields.discarded_products_results] = discarded_products[nm.Fields.end_use_in_use] * discarded_products[nm.Fields.discard_destination_ratio]
        
        self.print_debug_df(discarded_products)

        return

    def calculate_dispositions(self):
        return

    def calculate_fuel_burned(self):
        return

    def calculate_discarded_burned(self):
        return

    def fill_statistics(self):
        return

    def convert_emissions_c02_e(self):
        return

    def print_debug_df(self, df):
        """Print the head and tail of a DataFrame to console. Useful for testing

        Args:
            df (DataFrame): A DataFrame of interest to print
        """
        print(df.head())
        print(df.tail())




    