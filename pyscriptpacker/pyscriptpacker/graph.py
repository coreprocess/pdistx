import sys


class ModuleGraph(object):
    """
    Module graph tree used for detect import dependencies and order them
    if necessary.
    """

    BUILTIN_MODULES = sys.builtin_module_names

    def __init__(self):
        pass
