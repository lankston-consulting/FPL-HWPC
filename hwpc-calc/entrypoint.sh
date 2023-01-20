#!/bin/bash
# This mimics the dask docker image's prepare.sh
# It's possible the exec statement is needed to work 
# with tiny and exit properly

# -x
# Print a trace of simple commands, for commands, case commands, 
# select commands, and arithmetic for commands and their arguments 
# or associated word lists after they are expanded and before they 
# are executed. The value of the PS4 variable is expanded and the 
# resultant value is printed before the command and its expanded 
# arguments.
set -x

# Run extra commands
exec "$@"