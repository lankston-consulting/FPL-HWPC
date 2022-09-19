import hwpccalc.config
import hwpccalc.meta_model

# from hwpc import input_download
from hwpccalc.hwpc import names

# from hwpc import email


def run(path="hwpc-user-inputs/c6f40afe-b532-49d1-96e1-c45898a50e35", name="cali2"):

    names.Names()
    names.Names.Tables()
    names.Names.Fields()
    names.Names.Output()

    names.Names.Output.output_path = path.replace("inputs", "outputs")
    names.Names.Output.run_name = name

    # i = input_download.InputDownload()
    # i.downloads()
    me = hwpccalc.meta_model.MetaModel()

    me.run_simulation()

    # e = email.Email()
    # e.send_email(str(m.md.data['email'].columns.values[0]))

    print("model finished.")

    return


if __name__ == "__main__":
    run()
