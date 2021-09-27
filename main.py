import argparse

from hwpc import model, model_data, input_download, results
import config

def run(args):
    i = input_download.InputDownload()
    i.downloads(args.i)

    m = model.Model()
    m.run()

    m.md.pickle()
    m.results.pickle()

    md = model_data.ModelData.unpickle()

    r = results.Results.unpickle()
    r.total_yearly_harvest()

    print('model finished.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-i', 
        help='Path to the uploaded user data.', 
        default='hpwc-user-inputs/user_request_20210927_193455/user_input.json',
    )
    
    args, _ = parser.parse_known_args()

    run(args)
