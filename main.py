from hwpc import model, input_download
from config import gch

if __name__ == '__main__':

    # i = input_download.Input_Download()
    # i.downloads()

    m = model.Model()
    m.run()

    print('model finished.')
