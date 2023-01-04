import argparse
import os
import sys
import traceback

from dotenv import load_dotenv

import hwpccalc.config
import hwpccalc.meta_model
from hwpccalc.hwpc import names
from hwpccalc.utils import email

load_dotenv()

_debug_mode = bool(os.getenv("DEBUGGING"))
_debug_default_path = "t2023-01-03-01-2023T12:23:02"
_debug_default_name = "t2023-01"


def run(args: argparse.Namespace) -> int:
    """Main entrypoint for the HPWC simulation.
    
    Args:
        args: A set of parsed arguments from argparse.

    Returns:
        0 or 1, corresponding to exit codes.
    """
    path = args.path
    name = args.name

    names.Names()
    names.Names.Tables()
    names.Names.Fields()
    names.Names.Output()

    names.Names.Output.input_path = path
    names.Names.Output.output_path = path.replace("inputs", "outputs")
    names.Names.Output.run_name = name

    try:
        me = hwpccalc.meta_model.MetaModel()
    except Exception as last_ex:
        _handle_exception("Exception instantiating MetaModel.", last_ex)

    try:
        me.run_simulation()
    except Exception as last_ex:
        _handle_exception("Exception running simulation.", last_ex)

    print("model finished.")

    try:
        if not _debug_mode:
            mail = email.Email()
            mail.send_email()
        else:
            print(f"http://localhost:8080/output?p={_debug_default_path}&q={_debug_default_name}")
    except Exception as last_ex:
        _handle_exception("Exception sending notification email to user.", last_ex)

    return 0


def _handle_exception(msg: str, ex: Exception):
    """Helper function for repetitive exception reporting code.
    Prints a message (developer defined) and the exception that was raised. Exits the program.

    Args:
        msg (str): A descriptive message to indicate where this exception occured.
        ex (Exception): The Exception object that was created and caught.

    Returns:
        Does not return, exits the program.
    """
    print(msg)
    print(ex)
    print(traceback.print_exception(ex))
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    print("Client has been started. Beginning execution.")

    parser.add_argument("-b", "--bucket", help="Bucket to use for user input", default="hwpc")

    if _debug_mode:
        parser.add_argument("-p", "--path", help="Path to uploaded user data to run on", default=_debug_default_path)
        parser.add_argument("-n", "--name", help="User provided name of simulation run.", default=_debug_default_name)
    else:
        parser.add_argument("-p", "--path", help="Path to uploaded user data to run on", required=True)
        parser.add_argument("-n", "--name", help="User provided name of simulation run.", required=True)

    args, _ = parser.parse_known_args()

    try:
        run(args)
    except Exception as ex:
        _handle_exception("Uncaught error in HWPC-CALC", ex)
