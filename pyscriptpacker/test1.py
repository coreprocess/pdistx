import builtins

orig_import = builtins.__import__


def new_import(name, globals=None, locals=None, fromlist=(), level=0):
    print(
        f"name={name} fromlist=({', '.join(list(fromlist) if fromlist else [])}) level={level}"
    )
    m = orig_import(name, globals, locals, fromlist, level)
    print(f" -> {str(m)}")
    return m


builtins.__import__ = new_import

import os.path
import os.path as test1

print(f" -> test1 = {str(test1)}")

from os import path
from os import path as test2

print(f" -> test2 = {str(test2)}")
