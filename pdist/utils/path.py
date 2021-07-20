from fnmatch import fnmatch
from pathlib import Path
from shutil import rmtree
from typing import List


def fnmatch_any(name: str, patterns: List[str]):
    for pattern in patterns:
        if fnmatch(name, pattern):
            return True
    return False


def rmpath(path: Path):
    if path.exists():
        if path.is_dir():
            rmtree(path)
        else:
            path.unlink()
