import os
import platform
import sys

import psutil
from fastapi import APIRouter, status

router = APIRouter()

_REDACTED = "***REDACTED***"
_SENSITIVE_KEY_MARKERS = (
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "KEY",
    "CREDENTIAL",
    "AUTH",
    "DATABASE_URL",
    "DB_URL",
    "_URI",
    "_DSN",
)


def _redact_env_value(key: str, value: str) -> str:
    upper_key = key.upper()
    if any(marker in upper_key for marker in _SENSITIVE_KEY_MARKERS):
        return _REDACTED
    # Redact values that embed credentials, e.g. scheme://user:password@host
    if "://" in value and "@" in value:
        return _REDACTED
    return value


@router.get("/debug", status_code=status.HTTP_200_OK)
def get_debug_info_service():
    os_info = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

    env_vars = {key: _redact_env_value(key, value) for key, value in os.environ.items()}
    local_paths = {
        "current_working_directory": os.getcwd(),
        "sys_path": sys.path,
        "cwd_listing": os.listdir(os.getcwd()),
    }

    disk_usage = psutil.disk_usage(os.getcwd())
    disk_info = {
        "total": disk_usage.total,
        "used": disk_usage.used,
        "free": disk_usage.free,
        "percent": disk_usage.percent,
    }

    mem = psutil.virtual_memory()
    memory_info = {
        "total": mem.total,
        "available": mem.available,
        "used": mem.used,
        "free": mem.free,
        "percent": mem.percent,
    }

    debug_info = {
        "os_info": os_info,
        "env_vars": env_vars,
        "local_paths": local_paths,
        "disk_usage": disk_info,
        "memory_usage": memory_info,
    }

    return debug_info
