setup_code = '''
import json
import hashlib
import sys
import imp
try:
    import __builtin__ as builtins
except ImportError:
    import builtins

_bundle_hash = hashlib.sha256(
    json.dumps(_virtual_modules, sort_keys=True).encode('utf-8')).hexdigest()

print('Packer: init bundle_hash={{}}'.format(_bundle_hash))


def _try_load_module(name, local_name, parent_name, override):

    # qualified names
    qf_name = '{{}}.{{}}'.format(__name__, name)
    qf_parent_name = '{{}}.{{}}'.format(
        __name__, parent_name) if parent_name else __name__

    # check if module is not loaded already and available
    virtual_module = _virtual_modules.get(name, None)
    if not virtual_module or qf_name in sys.modules:
        return
    if not override:
        if hasattr(sys.modules[qf_parent_name], local_name):
            return

    # debug
    print(
        'Packer: loading name={{}}, qf_name={{}}, local_name={{}}, parent_name={{}}, qf_parent_name={{}}, override={{}}'
        .format(
            name,
            qf_name,
            local_name,
            parent_name,
            qf_parent_name,
            override,
        ))

    # create module object
    module = sys.modules[qf_name] = imp.new_module(qf_name)
    setattr(module, '__packer_bundle_hash__', _bundle_hash)
    module.__name__ = qf_name
    if virtual_module['is_package']:
        module.__package__ = qf_name
        module.__path__ = ['{{}}/{{}}'.format(_bundle_hash, name)]
    else:
        module.__package__ = sys.modules[qf_parent_name].__package__

    # import hook for modules using __import__ the wrong way
    def _packer_import_hook(name, globals=None, locals=None, fromlist=(), level=0):
        return _packer_import(
            name,
            globals if globals is not None else module.__dict__,
            locals if locals is not None else module.__dict__,
            fromlist,
            level,
        )

    setattr(module, '__import__', _packer_import_hook)

    # inject code
    exec(virtual_module['code'], module.__dict__)

    # link to parent
    setattr(sys.modules[qf_parent_name], local_name, module)


def _try_get_module_all_list(name):
    qf_name = '{{}}.{{}}'.format(__name__, name) if name else __name__
    module = sys.modules.get(qf_name, None)
    if module:
        all_list = getattr(module, '__all__', None)
        if all_list:
            return all_list
    return []


_orig_import = builtins.__import__


def _packer_import(name, globals=None, locals=None, fromlist=(), level=0):

    globals_or_empty = globals if globals else {{}}

    # determine load path
    if level > 0:
        load_path = globals_or_empty.get(
            '__package__',
            globals_or_empty['__name__'],
        ).split('.')
        if level > 1:
            load_path = load_path[:-(level - 1)]
    else:
        load_path = []
    load_path += name.split('.') if name else []

    # handle hoisted requests with rebased path
    if '.'.join(load_path) == __name__ or '.'.join(load_path).startswith(
            __name__ + '.'):
        load_path = load_path[len(__name__.split('.')):]

    # skip load requests not originating from the bundle
    elif globals_or_empty.get('__packer_bundle_hash__', None) != _bundle_hash:
        load_path = None

    # try to load and return module if load path is given
    if load_path is not None:

        # load modules along the path
        for depth in range(len(load_path)):
            _try_load_module(
                '.'.join(load_path[0:depth + 1]),
                load_path[depth],
                '.'.join(load_path[0:depth]) if depth > 0 else None,
                True,
            )

        # load modules referenced by the from list
        if fromlist:
            for from_item in fromlist:
                if from_item == '*':
                    all_list = _try_get_module_all_list(
                        '.'.join(load_path) if load_path else None,
                    )
                    for all_item in all_list:   
                        _try_load_module(
                            '.'.join(load_path + [all_item]),
                            all_item,
                            '.'.join(load_path) if load_path else None,
                            False,
                        )
                _try_load_module(
                    '.'.join(load_path + [from_item]),
                    from_item,
                    '.'.join(load_path) if load_path else None,
                    False,
                )

        # try to return the requested module
        if load_path:
            if not fromlist:
                return_name = '{{}}.{{}}'.format(__name__, load_path[0])
            else:
                return_name = '{{}}.{{}}'.format(__name__, '.'.join(load_path))

            if return_name in sys.modules:
                return sys.modules[return_name]

    # delegate import to original routine
    return _orig_import(name, globals, locals, fromlist, level)


builtins.__import__ = _packer_import


if sys.version_info >= (3, 0):

    # If we import this library in Python 2.x, the library can no longer be
    # imported by other modules. Weird behaviour, we would like to avoid.
    # So keep this import here!
    import importlib

    class _PackerLoader(importlib.abc.Loader):

        def __init__(self, code):
            self.code = code

        def create_module(self, spec):
            return None

        def exec_module(self, module):
            exec(self.code, module.__dict__)

    class _PackerMetaFinder(importlib.abc.MetaPathFinder):

        def find_spec(self, fullname, path, target=None):

            # construct load path
            load_path = fullname.split('.')

            # handle hoisted requests with rebased path
            if '.'.join(load_path).startswith(__name__ + '.'):
                load_path = load_path[len(__name__.split('.')):]

            # skip load requests not originating from the bundle
            elif not path or not path[0].startswith(
                    '{{}}/'.format(_bundle_hash)):
                return None

            # load module
            virtual_name = '.'.join(load_path)
            virtual_module = _virtual_modules.get(virtual_name, None)
            if not virtual_module:
                return None

            # create spec
            return importlib.util.spec_from_loader(
                virtual_name,
                loader=_PackerLoader(virtual_module['code']),
                is_package=True if virtual_module['is_package'] else None,
            )

    sys.meta_path.insert(0, _PackerMetaFinder())
'''


def get_setup_code():
    return setup_code.format()
