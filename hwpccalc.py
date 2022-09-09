import config

from hwpc import model
from hwpc import input_download
from hwpc import names

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

    me.run_simulation_dask()

    # e = email.Email()
    # e.send_email(str(m.md.data['email'].columns.values[0]))

    print("model finished.")

    return


if __name__ == "__main__":
    run()
