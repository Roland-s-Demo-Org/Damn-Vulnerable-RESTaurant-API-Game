import re
import shlex
import subprocess

# Argument-less "df" options that are safe to forward.
ALLOWED_DF_OPTIONS = {
    "-a",
    "--all",
    "-h",
    "--human-readable",
    "-H",
    "--si",
    "-i",
    "--inodes",
    "-k",
    "-l",
    "--local",
    "-P",
    "--portability",
    "-T",
    "--print-type",
    "--total",
}

# Conservative file system path / device pattern (no shell metacharacters).
_PATH_PATTERN = re.compile(r"^/[A-Za-z0-9_./@:+,=-]*$")


class InvalidDiskUsageParameters(ValueError):
    pass


def _parse_df_parameters(parameters: str):
    try:
        tokens = shlex.split(parameters or "")
    except ValueError:
        raise InvalidDiskUsageParameters("Invalid parameters")

    options = []
    paths = []
    for token in tokens:
        if token.startswith("-"):
            if token not in ALLOWED_DF_OPTIONS:
                raise InvalidDiskUsageParameters("Unsupported df option")
            options.append(token)
        elif _PATH_PATTERN.match(token):
            paths.append(token)
        else:
            raise InvalidDiskUsageParameters("Invalid path")

    return options, paths


def get_disk_usage(parameters: str):
    options, paths = _parse_df_parameters(parameters)
    command = ["df", "-h"] + options + ["--"] + paths

    try:
        # No shell and a minimal environment so that application secrets
        # (e.g. JWT_SECRET_KEY) are never inherited by the child process.
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env={"PATH": "/usr/local/bin:/usr/bin:/bin", "LC_ALL": "C"},
        )
        usage = result.stdout.strip().decode()
    except:
        raise Exception("An unexpected error was observed")

    return usage
