setup_code = '''
import sys
import imp
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

_orig_import = builtins.__import__

def _load_module(name, local_name, parent_name, override):

    # prefixed names
    prefixed_name = '{prefix}_{{}}'.format(name)
    prefixed_parent_name = '{prefix}_{{}}'.format(parent_name) if parent_name else None

    # check if module is not loaded already and available
    virtual_module = _virtual_modules.get(name, None)
    if not virtual_module or prefixed_name in sys.modules:
        return
    if not override and parent_name:
        if hasattr(sys.modules[prefixed_parent_name], local_name):
            return

    # debug
    print('Packer: loading name={{}}, prefixed_name={{}}, local_name={{}}, parent_name={{}}, prefixed_parent_name={{}}, override={{}}'.format(
        name,
        prefixed_name,
        local_name,
        parent_name,
        prefixed_parent_name,
        override,
    ))

    # create module object
    module = sys.modules[prefixed_name] = imp.new_module(name)
    module.__name__ = prefixed_name
    if virtual_module['is_package'] or not parent_name:
        module.__package__ = prefixed_name
        module.__path__ = []
    else:
        module.__package__ = sys.modules[prefixed_parent_name].__package__

    # inject code
    exec(virtual_module['code'], module.__dict__)

    # link to parent
    if parent_name:
        setattr(sys.modules[prefixed_parent_name], local_name, module)


def _hoist_module(name, hoist_base):

    # names
    prefixed_name = '{prefix}_{{}}'.format(name)
    hoisted_name = '{{}}.{{}}'.format(hoist_base, name)

    # hoist module
    module = sys.modules.get(prefixed_name, None)
    if module:
        print('Packer: hoisting name={{}}, prefixed_name={{}}, hoisted_name={{}}'.format(
            name,
            prefixed_name,
            hoisted_name,
        ))
        sys.modules[hoisted_name] = module


def _custom_import(name, globals=None, locals=None, fromlist=(), level=0):

    # determine absolute name
    if level > 0:
        path = globals.get('__package__', globals['__name__']).split('.')
        if level > 1:
            path = path[:-(level-1)]
    else:
        path = []
    path += name.split('.') if name else []

    # handle prefixed modules
    if path[0].startswith('{prefix}_'):
        path[0] = path[0][len('{prefix}_'):]

    # handle hoisted modules
    elif '.'.join(path).startswith(__name__ + '.'):
        path = path[len(__name__.split('.')):]

    # skip module loading in all other cases
    else:
        path = None

    # load virtual modules
    if path:
        for depth in range(len(path)):
            _load_module(
                '.'.join(path[0:depth + 1]),
                path[depth],
                '.'.join(path[0:depth]) if depth > 0 else None,
                True,
            )
            _hoist_module(
                '.'.join(path[0:depth + 1]),
                __name__,
            )

        if path and fromlist:
            for from_item in fromlist:
                if from_item == '*':
                    continue
                _load_module(
                    '.'.join(path + [from_item]),
                    from_item,
                    '.'.join(path),
                    False,
                )
                _hoist_module(
                    '.'.join(path + [from_item]),
                    __name__,
                )
    
    # delegate actual task to original import routine
    return _orig_import(name, globals, locals, fromlist, level)


builtins.__import__ = _custom_import
'''


def get_setup_code(prefix):
    return setup_code.format(prefix=prefix)
