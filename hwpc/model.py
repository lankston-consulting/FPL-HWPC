import model_data

class Model(object):

    def __init__(self) -> None:
        super().__init__()

        self.data = model_data.ModelData()
        self.data.load_data()

    def run(self, iterations=1):


        return



    