#!/usr/bin/env python
import os

from dotenv import load_dotenv

# from lcutils import gcs

load_dotenv()

###############################################################################
#                               Initialization.                               #
###############################################################################
# storage_keyfile = os.getenv("CS_SA_KEY_FILE")

# if storage_keyfile is not None and os.path.exists(storage_keyfile):
#     gch = gcs.GcsTools(use_service_account={"keyfile": storage_keyfile})
# else:
#     gch = gcs.GcsTools()
