import numpy as np

from hwpc import model_data

class Model(object):

    def __init__(self) -> None:
        super().__init__()

        self.data = model_data.ModelData()
        self.data.load_data()

        self.timber_product_ratios = self.data['timber_product_data']
        self.timber_product_ratios = self.data['timber_product_data']
        self.timber_product_ratios = self.data['timber_product_data']
        self.timber_product_ratios = self.data['timber_product_data']
        self.timber_product_ratios = self.data['timber_product_data']
        

        # number of years in model
        self.num_years = 0

        # number of timber products
        self.num_timber_products = 0

        # number of primary products
        self.num_primary_products = 0

        # the amount of product that is not lost
        self.end_use_loss_factor = 0.92

        # default percent of product that is burned with energy capture
        self.default_burned_energy_capture = 0

    def run(self, iterations=1):

        years = self.data.get_harvest_years(self)

        # TODO convert from mbf to ccf if needed

        return

    def calculate_primary_product_mcg(self):
        """Calculate the amounts of primary products (MgC) harvested in each year.
        """

        # Calculate timber products (CCF) by multiplying the harvest-to-timber ratio for each
        # timber product by the amount harvested that year.
        timber_products_ccf = np.array(self.numTimberProducts, self.numYears)
        for p in range(self.num_timber_products):
            for y in range(self.num_years):
                timber_products_ccf[p, y] = this.timberProductRatios[p, y] * this.harvests[y]
            
        # Calculate primary products (CCF) by multiplying the timber-to-primary ratio for each 
        # primary product by the amount of the corresponding timber product. Then convert to MgC
        # by multiplying by the CCF-to-MgC ratio for that primary product.
        


        for (int p = 0; p < this.numPrimaryProducts; p++)
            {
                for (int y = 0; y < this.numYears; y++)
                {
                    this.primaryProducts[p, y] = this.ccfToMgcRatios[p] *
                        this.primaryProductRatios[p, y] *
                        timberProductsCcf[this.primaryToTimberMap[p], y];
                }
            }
        return

    def calculate_end_use_products(self):
        """Calculate the amount of end use products harvested in each year.
        """

        # Multiply the primary-to-end-use ratio for each end use product by the amount of the
        # corresponding primary product.
        return

    def calculate_products_in_use(self):
        """Calculate the amount of end use products from each vintage year that are still in use
        during each inventory year.
        """
        return

    def calculate_discarded_dispositions(self):
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





    