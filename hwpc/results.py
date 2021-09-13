import pandas as pd

class Results(object):

    def __init__(self) -> None:
        super().__init__()

        self.working_table = None

        self.total_dispositions = None

        self.fuel_captured = None

    def save_results(self):
        self.working_table.to_csv('results.csv')
        return
      
