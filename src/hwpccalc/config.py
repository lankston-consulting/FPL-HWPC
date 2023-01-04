#!/usr/bin/env python
import os

from dotenv import load_dotenv

load_dotenv()

_debug_mode_raw = os.getenv("HWPC__DEBUG__MODE")
_debug_mode = False

if _debug_mode_raw.lower().find("t") >= 0 or _debug_mode_raw.lower().find("1") >= 0:
    _debug_mode = True
