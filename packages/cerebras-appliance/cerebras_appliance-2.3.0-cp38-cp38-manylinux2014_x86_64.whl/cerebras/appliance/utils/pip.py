# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""
utils file for miscellaneous pip functions
"""
import subprocess
import sys
from typing import List


def pip_config_list() -> str:
    """Returns pip config options"""
    args = [sys.executable, "-m", "pip", "config", "list"]
    p = subprocess.run(args, check=True, capture_output=True)
    config_outputs = p.stdout.decode().split("\n")

    pip_options = ""
    for line in config_outputs:
        if '=' not in line:
            continue
        key, val = line.split('=', 1)
        if 'index-url' in key and 'extra-index-url' not in key:
            pip_options += f"--index-url {val.strip()} "
        elif 'extra-index-url' in key:
            pip_options += f"--extra-index-url {val.strip()} "
        elif 'trusted-host' in key:
            pip_options += f"--trusted-host {val.strip()} "
        elif 'timeout' in key:
            timeout = val.strip().replace("'", "")
            pip_options += f'--timeout {timeout} '
    return pip_options.strip()


def pip_freeze() -> List[str]:
    """Returns formatted output from pip freeze to capture current env"""
    args = [sys.executable, "-m", "pip", "freeze"]
    p = subprocess.run(args, check=True, capture_output=True)
    freeze_outputs = p.stdout.decode().split("\n")

    dependencies = []
    for package_requirement in freeze_outputs:
        if '==' in package_requirement:
            dependencies.append(package_requirement)
        elif ' @ ' in package_requirement:
            key, val = package_requirement.split(' @ ', 1)
            dependencies.append(f"{key}@{val}")
        else:
            # We don't expect anything else here, but let's pass it through as is
            dependencies.append(package_requirement)

    return dependencies
