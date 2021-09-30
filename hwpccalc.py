import argparse
import config

from hwpc import model
from hwpc import model_data
from hwpc import input_download
from hwpc import names
from hwpc import results

def run(args):

    names.Names()
    names.Names.Tables()
    names.Names.Fields()
    names.Names.Output()

    names.Names.Output.output_path = args.i

    i = input_download.InputDownload()
    i.downloads()

    m = model.Model()

    m.run()

    m.md.pickle()
    m.results.pickle()

    md = model_data.ModelData.unpickle()

    r = results.Results.unpickle()
    r.total_yearly_harvest()

    print('model finished.')

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-i', 
        help='Path to the uploaded user data.', 
        default='hpwc-user-inputs/user_request_20210929_130704',
    )
    
    args, _ = parser.parse_known_args()

    run(args)
