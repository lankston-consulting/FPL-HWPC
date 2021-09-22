import pandas as pd
import matplotlib.pyplot as plt
from hwpc.names import Names as nm

class Results(object):

    def __init__(self) -> None:
        super().__init__()

        self.working_table = None

        self.total_dispositions = None

        self.fuel_captured = None

        self.end_use_products_step = None

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

        # burned = burned.groupby(by="Year")[['discarded_products_adjusted','DiscardDestinationRatio']]
        # burned = burned.agg(burned)
        # burned.to_csv('total_dispositions_0.csv')
        # plt.title("Total Cumulative Carbon in End Use Products in Use")
        # plt.xlabel('Years')
        # plt.ylabel('Metric Tons C (10^6)')
        # plt.plot(burned)
        # plt.show()
        

        recycled = recycled.groupby(by="Year")[nm.Fields.carbon].sum()
        recycled.to_csv('total_dispositions.csv')
        plt.title('total carbon recycled')
        plt.xlabel('Years')
        plt.ylabel('Products (ccf)')
        plt.plot(recycled)
        plt.show()

        # composted = composted.groupby(by="Year")[nm.Fields.running_discarded_products].sum()
        # composted.to_csv('total_dispositions_2.csv')
        # plt.xlabel('Years')
        # plt.ylabel('Products (ccf)')
        # plt.plot(composted)
        # plt.show()

        landfills_carbon = landfills.groupby(by="Year")[nm.Fields.carbon].sum()
        landfills_carbon.to_csv('total_dispositions_3.csv')
        plt.title("total cabon landfills")
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(landfills_carbon)
        plt.show()

        landfills_emit = landfills.groupby(by="Year")[nm.Fields.co2].sum()
        landfills_emit.to_csv('total_dispositions_3.csv')
        plt.title("total cabon emit landfills")
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C')
        plt.plot(landfills_emit)
        plt.show()

        
        # dumps = dumps.groupby(by="Year")[nm.Fields.running_discarded_products].sum()
        # dumps.to_csv('total_dispositions_4.csv')
        # plt.xlabel('Years')
        # plt.ylabel('Products (ccf)')
        # plt.plot(dumps)
        # plt.show()

        #self.total_dispositions.to_csv('total_dispositions.csv')
        return
    
    def save_fuel_captured(self):
        # print(self.fuel_captured.axes)
        # fc = pd.DataFrame(self.fuel_captured)
        # fc_total_fuel_captured = fc.groupby(by="Year")['burned_captured'].sum()
        # plt.xlabel('Years')
        # plt.ylabel("Burned Captured (ccf)")
        # plt.plot(fc_total_fuel_captured)
        # plt.show()
        # self.fuel_captured = self.fuel_captured.cumsum(Index='burn_caputured')
        # fc_total_fuel_captured.to_csv('fuel_captured.csv')
        return
    
    def save_end_use_products(self):
        # self.end_use_products_step.to_csv('end_use_products.csv')
        return
