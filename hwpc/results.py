import pandas as pd

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
        print(self.total_dispositions.axes)
        #self.total_dispositions = self.total_dispositions.cumsum(axis=0)
        self.total_dispositions.to_csv('total_dispositions.csv')
        return
    
    def save_fuel_captured(self):
        print(self.fuel_captured.axes)
        #self.fuel_captured = self.fuel_captured.cumsum(Index='burn_caputured')
        self.fuel_captured.to_csv('fuel_captured.csv')
        return
    
    def save_end_use_products(self):
        self.end_use_products_step.to_csv('end_use_products.csv')
        return
