import argparse
import os
import sys
import traceback

import hwpccalc.config
import hwpccalc.meta_model
from hwpccalc.hwpc import names
from hwpccalc.utils import email


_debug_mode = hwpccalc.config._debug_mode
_debug_default_path = os.getenv("HWPC__DEBUG__PATH")
_debug_default_name = os.getenv("HWPC__DEBUG__NAME")


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

    try:
        me = hwpccalc.meta_model.MetaModel(input_path=path, run_name=name)
    except Exception as last_ex:
        _handle_exception("Exception instantiating MetaModel.", last_ex)

    try:
        user_info = me.run_simulation()
    except Exception as last_ex:
        traceback.print_exc()
        _handle_exception("Exception running simulation.", last_ex)

    print("model finished.")

    try:
        if _debug_mode:
            print(f"http://localhost:8080/output?p={path}&q={name}")
        else:
            email.Email().send_email(
                email_address=user_info["email_address"], user_string=user_info["user_string"], scenario_name=user_info["scenario_name"]
            )
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
    print("msg:", msg)
    print("ex:", ex)
    # try:
    print("traceback follows:")
    traceback.print_exc()
    # except TypeError as te:
    #     # Passing "ex" to traceback.print_exception was introduced in Python 3.10.
    #     # Use old method if it fails.
    #     print(traceback.print_exception(value=ex))
    print("Sending SIGEXIT (1)")
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    print("Container has been started. Beginning execution.")

    parser.add_argument("-b", "--bucket", help="Bucket to use for user input", default="hwpc")

    if _debug_mode:
        parser.add_argument("-p", "--path", help="Path to uploaded user data to run on", default=f"{_debug_default_path}")
        parser.add_argument("-n", "--name", help="User provided name of simulation run.", default=f"{_debug_default_name}")
    else:
        parser.add_argument("-p", "--path", help="Path to uploaded user data to run on", required=True)
        parser.add_argument("-n", "--name", help="User provided name of simulation run.", required=True)

    args, _ = parser.parse_known_args()

    try:
        run(args)
    except Exception as ex:
        _handle_exception("Uncaught error in hwpc-calc", ex)
    finally:
        sys.exit(0)
