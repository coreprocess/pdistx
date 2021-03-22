setup_code = '''
import sys
import imp
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

_orig_import = builtins.__import__


def inject_module(name, local_name, parent_name, override):
    # check if module is not loaded already and available
    virtual_module = _virtual_modules.get(name, None)
    if not virtual_module or name in sys.modules:
        return
    if not override and parent_name:
        if hasattr(sys.modules[parent_name], local_name):
            return

    # print loading procedure
    print('Packer: loading name={}, local_name={}, parent_name={}, override={}'.format(
        name,
        local_name,
        parent_name,
        override,
    ))

    # create module object
    module = sys.modules[name] = imp.new_module(name)
    module.__name__ = name
    if virtual_module['is_package'] or not parent_name:
        module.__package__ = name
        module.__path__ = []
    else:
        module.__package__ = sys.modules[parent_name].__package__

    # inject code
    exec(virtual_module['code'], module.__dict__)

    # link to parent
    if parent_name:
        setattr(sys.modules[parent_name], local_name, module)


def custom_import(name, globals=None, locals=None, fromlist=(), level=0):

    # determine absolute name
    if level > 0:
        path = globals.get('__package__', globals['__name__']).split('.')
        if level > 1:
            path = path[:-(level-1)]
    else:
        path = []
    path += name.split('.') if name else []

    # import virtual modules
    for depth in range(len(path)):
        inject_module(
            '.'.join(path[0:depth + 1]),
            path[depth],
            '.'.join(path[0:depth]) if depth > 0 else None,
            True,
        )

    if path and fromlist:
        for from_item in fromlist:
            if from_item == '*':
                continue
            inject_module(
                '.'.join(path + [from_item]),
                from_item,
                '.'.join(path),
                False,
            )

    # delegate actual task to original import routine
    return _orig_import(name, globals, locals, fromlist, level)


builtins.__import__ = custom_import
'''


def get_setup_code():
    return setup_code
