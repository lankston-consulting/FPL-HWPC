from pydoc import doc
import config

from hwpc import model
from hwpc import input_download
from hwpc import names

from distributed import get_client


# from hwpc import email


def run(path="hpwc-user-inputs/c6f40afe-b532-49d1-96e1-c45898a50e35", name="cali2"):

    names.Names()
    names.Names.Tables()
    names.Names.Fields()
    names.Names.Output()

    names.Names.Output.output_path = path
    names.Names.Output.run_name = name

    # i = input_download.InputDownload()
    # i.downloads()
    me = model.Meta()

    # me.run_simulation()
    me.run_simulation_dask()

    # client = get_client()
    # print(len(client.get_events("New Sim")))
    # v = client.get_events("New Sim")

    # last_k = None
    # while True:
    #     ks = list(me.model_collection)
    #     if last_k == ks:
    #         break
    #     for k in ks:
    #         if last_k is None or k not in last_k:
    #             me.model_collection[k].run()
    #     last_k = ks

    # i = 1

    # e = email.Email()
    # e.send_email(str(m.md.data['email'].columns.values[0]))
    
    print('model finished.')

    return


if __name__ == "__main__":
    run()
