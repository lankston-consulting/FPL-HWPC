from hwpc import model, input_download, results
from config import gch

if __name__ == '__main__':

    # i = input_download.InputDownload()
    # i.downloads()

    # m = model.Model()
    # m.run()

    r = results.Results()
    r.load_results()

    r.total_yearly_harvest()

    print('model finished.')
