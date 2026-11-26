import os
import platform
import sys

import psutil
from fastapi import APIRouter, status

router = APIRouter()

_SENSITIVE_MARKERS = (
    "PASSWORD",
    "PASSWD",
    "SECRET",
    "TOKEN",
    "KEY",
    "CREDENTIAL",
    "AUTH",
    "DATABASE_URL",
    "DB_URL",
    "DSN",
)


def _is_sensitive(name: str) -> bool:
    upper = name.upper()
    return any(marker in upper for marker in _SENSITIVE_MARKERS)


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

    # Defense in depth: never return secret values, even to authorized callers.
    env_vars = {
        key: ("[REDACTED]" if _is_sensitive(key) else value)
        for key, value in os.environ.items()
    }
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
