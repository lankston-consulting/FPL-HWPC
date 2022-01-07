import argparse
import config

from hwpc import model
from hwpc import model_data
from hwpc import input_download
from hwpc import names
from hwpc import results
from hwpc import email

def run(path='hpwc-user-inputs/3097a3de-5fc0-4f16-988f-cd739e08ac4e', name='robbdemo3'):

    path = path
    names.Names()
    names.Names.Tables()
    names.Names.Fields()
    names.Names.Output()
    
    names.Names.Output.output_path = path
    names.Names.Output.run_name = name

    i = input_download.InputDownload()
    i.downloads()

   



    m = model.Model()

    m.run()

    e = email.Email()
    e.send_email(str(m.md.data['email'].columns.values[0]))
    print('model finished.')

    return

if __name__ == '__main__':
    run()