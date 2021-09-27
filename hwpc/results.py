import pandas as pd
import pickle
import matplotlib.pyplot as plt
from hwpc import model_data
from hwpc.names import Names as nm
from utils import pickler


class Results(pickler.Pickler):

    def __init__(self) -> None:
        super().__init__()

        self.timber_products = None
        self.primary_products = None
        self.end_use_products = None
        self.products_in_use = None
        self.discarded_products = None
        self.discarded_wood_paper = None
        self.dispositions = None

        self.working_table = None

        self.total_dispositions = None

        self.fuel_captured = None

        self.md = model_data.ModelData()

        return

    def save_results(self):
        self.working_table.to_csv('results.csv')
        return

    def save_total_dispositions(self):
        df = pd.DataFrame(self.working_table)
        # burned = df[df[nm.Fields.discard_destination_id] == 0] 
        recycled = df[df[nm.Fields.discard_destination_id] == 1]
        composted = df[df[nm.Fields.discard_destination_id] == 2]
        landfills = df[df[nm.Fields.discard_destination_id] == 3]
        dumps = df[df[nm.Fields.discard_destination_id] == 4]

        # burned = burned.groupby(by='Year')[['discarded_products_adjusted','DiscardDestinationRatio']]
        # burned = burned.agg(burned)
        # burned.to_csv('total_dispositions_0.csv')
        # plt.title('Total Cumulative Carbon in End Use Products in Use')
        # plt.xlabel('Years')
        # plt.ylabel('Metric Tons C (10^6)')
        # plt.plot(burned)
        # plt.show()

        cum_products = df.groupby(by='Year')[nm.Fields.running_discarded_products].sum()
        cum_products.to_csv('total_end_use_products.csv')
        plt.title('Total Cumulative Carbon in End Use Products in Use')
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(cum_products)
        plt.show()

        recycled_carbon = recycled.groupby(by='Year')[nm.Fields.carbon].sum()
        recycled_carbon.to_csv('total_recycled_carbon.csv')
        plt.title('Total Cumulative Carbon in Recovered Products in Use')
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(recycled_carbon)
        plt.show()

        recycled_emit = recycled.groupby(by='Year')[nm.Fields.co2].sum()
        recycled_emit.to_csv('total_recycled_emitted.csv')
        plt.title('Total Cumulative Cabon Emitted from Recovered Products')
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(recycled_emit)
        plt.show()

        # composted = composted.groupby(by='Year')[nm.Fields.running_discarded_products].sum()
        # composted.to_csv('total_dispositions_2.csv')
        # plt.xlabel('Years')
        # plt.ylabel('Products (ccf)')
        # plt.plot(composted)
        # plt.show()

        landfills_carbon = landfills.groupby(by='Year')[nm.Fields.carbon].sum()
        landfills_carbon.to_csv('total_landfills_carbon.csv')
        plt.title('Total Cumulative Cabon in Landfills')
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(landfills_carbon)
        plt.show()

        landfills_emit = landfills.groupby(by='Year')[nm.Fields.co2].sum()
        landfills_emit.to_csv('total_landfills_emitted.csv')
        plt.title('Total Cumulative Cabon Emitted from Landfills')
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(landfills_emit)
        plt.show()

        
        dumps_carbon = dumps.groupby(by='Year')[nm.Fields.carbon].sum()
        dumps_carbon.to_csv('total_dumps_carbon.csv')
        plt.title('Total Cumulative Cabon in Dumps')
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(dumps_carbon)
        plt.show()

        dumps_emit = dumps.groupby(by='Year')[nm.Fields.co2].sum()
        dumps_emit.to_csv('total_dumps_emit.csv')
        plt.title('Total Cumulative Cabon Emitted from Dumps')
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(dumps_emit)
        plt.show()

        #self.total_dispositions.to_csv('total_dispositions.csv')
        return
    
    def save_fuel_captured(self):
        # print(self.fuel_captured.axes)
        # fc = pd.DataFrame(self.fuel_captured)
        # fc_total_fuel_captured = fc.groupby(by='Year')['burned_captured'].sum()
        # plt.xlabel('Years')
        # plt.ylabel('Burned Captured (ccf)')
        # plt.plot(fc_total_fuel_captured)
        # plt.show()
        # self.fuel_captured = self.fuel_captured.cumsum(Index='burn_caputured')
        # fc_total_fuel_captured.to_csv('fuel_captured.csv')
        return
    
    def save_end_use_products(self):
        # self.end_use_products_step.to_csv('end_use_products.csv')
        return

    def total_yearly_harvest(self):

        df = pd.DataFrame(self.primary_products)
        print(self.md.data[nm.Tables.primary_products])
        df = df.merge(self.md.data[nm.Tables.primary_products], how='outer', on=[nm.Fields.timber_product_id, nm.Fields.primary_product_id])
        n = nm.Fields.c(nm.Fields.timber_product_results)
        print(df)
        # df[n] = df[nm.Fields.timber_product_results] * df[nm.Fields.conversion_factor]
        # df_sum = df.groupby(by=nm.Fields.harvest_year)[n].mode()


        return
