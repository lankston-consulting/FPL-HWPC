import argparse

import hwpccalc.config
import hwpccalc.meta_model
from hwpccalc.hwpc import names
from hwpccalc.utils import email


def run(args):

    path = args.path
    name = args.name

    names.Names()
    names.Names.Tables()
    names.Names.Fields()
    names.Names.Output()

    names.Names.Output.input_path = path
    names.Names.Output.output_path = path.replace("inputs", "outputs")
    names.Names.Output.run_name = name
    me = hwpccalc.meta_model.MetaModel()
    me.run_simulation()
    mail = email.Email()
    mail.send_email()

    print("model finished.")

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--bucket", help="Bucket to use for user input", default="hwpc")
    parser.add_argument("-p", "--path", help="Path to uploaded user data to run on", default="hwpc-user-inputs/601b159f-9526-4dd6-93a5-59fbdfc486cd")
    parser.add_argument("-n", "--name", help="User provided name of simulation run.", default="new-revision-test")

    args, _ = parser.parse_known_args()

    run(args)
