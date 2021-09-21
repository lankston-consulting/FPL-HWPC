import pandas as pd
import matplotlib.pyplot as plt

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
        df_end_use = df[df['DiscardDestinationID'] == 0]
        df_1 = df[df['DiscardDestinationID'] == 1]
        df_2 = df[df['DiscardDestinationID'] == 2]
        df_3 = df[df['DiscardDestinationID'] == 3]
        df_4 = df[df['DiscardDestinationID'] == 4]

        df_end_use = df_end_use.groupby(by="Year")[['discarded_products_adjusted','DiscardDestinationRatio']]
        df_end_use = df_end_use.agg(df_end_use)
        df_end_use.to_csv('total_dispositions_0.csv')
        plt.title("Total Cumulative Carbon in End Use Products in Use")
        plt.xlabel('Years')
        plt.ylabel('Metric Tons C (10^6)')
        plt.plot(df_end_use)
        plt.show()
        

        # df_1 = df_1.groupby(by="Year")['cum_discarded_products'].sum()
        # df_1.to_csv('total_dispositions_1.csv')
        # plt.xlabel('Years')
        # plt.ylabel('Products (ccf)')
        # plt.plot(df_1)
        # plt.show()

        # df_2 = df_2.groupby(by="Year")['cum_discarded_products'].sum()
        # df_2.to_csv('total_dispositions_2.csv')
        # plt.xlabel('Years')
        # plt.ylabel('Products (ccf)')
        # plt.plot(df_2)
        # plt.show()

        # df_3 = df_3.groupby(by="Year")['discard_dispositions'].sum()
        # df_3.to_csv('total_dispositions_3.csv')
        # plt.xlabel('Years')
        # plt.ylabel('Products (ccf)')
        # plt.plot(df_3)
        # plt.show()

        
        # df_4 = df_4.groupby(by="Year")['cum_discarded_products'].sum()
        # df_4.to_csv('total_dispositions_4.csv')
        # plt.xlabel('Years')
        # plt.ylabel('Products (ccf)')
        # plt.plot(df_4)
        # plt.show()

        #self.total_dispositions.to_csv('total_dispositions.csv')
        return
    
    def save_fuel_captured(self):
        #print(self.fuel_captured.axes)
        fc = pd.DataFrame(self.fuel_captured)
        fc_total_fuel_captured = fc.groupby(by="Year")['burned_captured'].sum()
        plt.xlabel('Years')
        plt.ylabel("Burned Captured (ccf)")
        plt.plot(fc_total_fuel_captured)
        plt.show()
        #self.fuel_captured = self.fuel_captured.cumsum(Index='burn_caputured')
        fc_total_fuel_captured.to_csv('fuel_captured.csv')
        return
    
    def save_end_use_products(self):
        self.end_use_products_step.to_csv('end_use_products.csv')
        return
