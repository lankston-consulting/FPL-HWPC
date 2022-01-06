#!/usr/bin/env python
import os
from dotenv import load_dotenv
from utils import user_data_helper
"""Credentials for RPMS App."""

load_dotenv()

###############################################################################
#                               Initialization.                               #
###############################################################################
json_keyfile = os.getenv('SERVICE_ACCOUNT_FILE')
print(os.environ)
if os.path.exists(json_keyfile):
    gch = user_data_helper.UserData(use_service_account={'keyfile': json_keyfile})
else:
    gch = user_data_helper.UserData()
