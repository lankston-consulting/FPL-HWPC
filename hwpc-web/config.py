#!/usr/bin/env python
import os

# from lcutils import gcs
from dotenv import find_dotenv, load_dotenv

# from utils import gcs_helper
"""Credentials for RPMS App."""

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

###############################################################################
#                               Initialization.                               #
###############################################################################
# json_keyfile = os.getenv('SERVICE_ACCOUNT_FILE')
# if os.path.exists(json_keyfile):
#     gch = gcs.GcsTools(use_service_account={'keyfile': json_keyfile})
# else:
#     gch = gcs.GcsTools()
