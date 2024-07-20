# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""Utilities for working with files and directories."""

import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, TypeVar, Union

from .units import ByteUnit, convert_byte_unit

StrPath = TypeVar("StrPath", bound=Union[str, os.PathLike])


def is_pathlike(name: Any) -> bool:
    """Returns True if the given name is a path-like object."""
    return isinstance(name, (str, Path))


def get_path_size(
    path: StrPath,
    unit: ByteUnit = "B",
    recurse: bool = False,
    raise_if_not_found: bool = True,
) -> Union[int, None]:
    """Get the size of a file or directory.

    Args:
        path: The path to the file or directory.
        unit: The unit to return the size in.
        recurse: If True, recurse into subdirectories and return the total size.
        raise_if_not_found: If True, raise an exception if the path does not
            exist.
    Returns:
        The size of the file or directory in the given unit.
    Raises:
        FileNotFoundError: If the path does not exist and `raise_if_not_found`
            is True.
    """
    p = Path(path)
    if not p.exists():
        if raise_if_not_found:
            raise FileNotFoundError(f"Path `{path}` does not exist")
        return None
    if p.is_file():
        return convert_byte_unit(p.stat().st_size, unit)
    if p.is_dir():
        return convert_byte_unit(
            sum(
                f.stat().st_size
                for f in p.glob("**/*" if recurse else "*")
                if f.is_file()
            ),
            unit,
        )
    else:
        raise ValueError(f"Path `{path}` is not a file or directory")


def create_symlink(src: Path, dst: Path, num_retries: int = 5, **kwargs):
    """Create symlink with retires in case of parallel runs."""
    for _ in range(num_retries):
        try:
            src.unlink(missing_ok=True)
            src.symlink_to(dst, **kwargs)
            break
        except OSError:
            time.sleep(0.5)
    else:
        # If still not working just error out
        src.unlink(missing_ok=True)
        src.symlink_to(dst, **kwargs)


@contextmanager
def short_temp_dir():
    """Set simpler temp directory in case current one exceeds AF_UNIX limit"""
    original_temp = os.environ.get("TMPDIR")
    try:
        os.environ.update({"TMPDIR": "/tmp/"})
        yield
    finally:
        if original_temp:
            os.environ.update({"TMPDIR": original_temp})
