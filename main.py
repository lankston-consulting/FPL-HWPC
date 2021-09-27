from hwpc import model, model_data, input_download, results
import config

if __name__ == '__main__':

    # i = input_download.InputDownload()
    # i.downloads()

    m = model.Model()
    m.run()

    m.md.pickle()
    m.results.pickle()

    md = model_data.ModelData.unpickle()

    r = results.Results.unpickle()
    r.total_yearly_harvest()

    print('model finished.')
