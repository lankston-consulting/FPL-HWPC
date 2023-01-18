#!/usr/bin/env python
import os
from os import environ as envs

from dotenv import find_dotenv, load_dotenv


class EnvValueError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

_debug_mode_raw = os.getenv("HWPC__DEBUG__MODE")
_debug_mode = False

if _debug_mode_raw is not None and (
    _debug_mode_raw.lower().find("y") >= 0 or _debug_mode_raw.lower().find("t") >= 0 or _debug_mode_raw.lower().find("1") >= 0
):
    _debug_mode = True


def validate_env():
    required_envs = [
        "HWPC__PURE_S3",
        "HWPC__CDN_URI",
        "HWPC__FIRST_RECYCLE_YEAR",
        "HWPC__RECURSE_LIMIT",
        "HWPC__DEBUG__MODE",
        "AWS_CONTAINER_IMG",
        "AWS_CLUSTER_ARN",
        "AWS_SECURITY_GROUP",
        "DASK_USE_FARGATE",
        "DASK_SCEDULER_CPU",
        "DASK_SCEDULER_MEM",
        "DASK_WORKER_CPU",
        "DASK_WORKER_MEM",
        "DASK_N_WORKERS",
    ]

    for re in required_envs:
        if envs[re] is None:
            raise EnvValueError(f'Missing required environment variable. "{re}" is required.')

    if _debug_mode:
        debug_envs = [
            "HWPC__DEBUG__START_YEAR",
            "HWPC__DEBUG__END_YEAR",
            "HWPC__DEBUG__PATH",
            "HWPC__DEBUG__NAME",
        ]

        for de in debug_envs:
            if envs[de] is None:
                raise EnvValueError(f'Debug mode requested. "{re}" environment variable is required.')


# validate_env()
