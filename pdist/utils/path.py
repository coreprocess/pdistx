from fnmatch import fnmatch
from typing import List


def fnmatch_any(name: str, patterns: List[str]):
    for pattern in patterns:
        if fnmatch(name, pattern):
            return True
    return False
