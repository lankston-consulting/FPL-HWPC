import argparse

import hwpccalc.config
import hwpccalc.meta_model
from hwpccalc.hwpc import names
from hwpccalc.utils import email


def run(args):
    """Main entrypoint for the HPWC simulation."""

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
<<<<<<< Updated upstream
    parser.add_argument("-p", "--path", help="Path to uploaded user data to run on", default="hwpc-user-inputs/r-cali-test")
    parser.add_argument("-n", "--name", help="User provided name of simulation run.", default="california_20221017")
=======
    parser.add_argument("-p", "--path", help="Path to uploaded user data to run on", default="hwpc-user-inputs/lambda-test-3-15-12-2022T23:59:27")
    parser.add_argument("-n", "--name", help="User provided name of simulation run.", default="lambda-test-3")
>>>>>>> Stashed changes

    args, _ = parser.parse_known_args()

    run(args)
