import argparse
import config

from hwpc import model
from hwpc import model_data
from hwpc import input_download
from hwpc import names
from hwpc import results

def run(path='hpwc-user-inputs/83d4b4ef-d57a-4995-8342-489ca4d769b3', name='test'):

    path = path
    names.Names()
    names.Names.Tables()
    names.Names.Fields()
    names.Names.Output()

    names.Names.Output.output_path = path
    names.Names.Output.run_name=name

    i = input_download.InputDownload()
    i.downloads()

    m = model.Model()

    m.run()

    print('model finished.')

    return

if __name__ == '__main__':
    run()