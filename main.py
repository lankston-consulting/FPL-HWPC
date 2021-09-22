from hwpc import model, input_download, results
from config import gch

if __name__ == '__main__':

    i = input_download.InputDownload()
    i.downloads()

    m = model.Model()
    m.run()

    m.results.pickle()

    r = results.Results.unpickle()
    r.total_yearly_harvest()

    print('model finished.')
