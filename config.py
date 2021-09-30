#!/usr/bin/env python
from utils import user_data_helper
"""Credentials for RPMS App."""


# The private key associated with your service account in JSON format.
GCP_PRIVATE_KEY_FILE = 'hwpc-sa.json'

###############################################################################
#                               Initialization.                               #
###############################################################################
gch = user_data_helper.UserData(use_service_account={'keyfile': GCP_PRIVATE_KEY_FILE})
#gch = user_data_helper.UserData()
