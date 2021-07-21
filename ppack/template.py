__pack_name__ = ''
__pack_hash__ = ''
__pack_token__ = ''


# pylint: disable=import-outside-toplevel,deprecated-module,exec-used
def __pack_loader__():

    # import all required modules
    import binascii
    import imp
    import os
    import os.path
    import sys

    # generate token
    global __pack_token__
    __pack_token__ = binascii.hexlify(os.urandom(8))

    # modules will be injected here
    modules = {}

    # determine resource root
    resource_root = os.path.splitext(__file__)[0] + '_resources'

    # determine module base
    if __name__ == '__main__':
        base = '{}_{}_{}'.format(__pack_name__, __pack_hash__, __pack_token__)
    else:
        base = '{}.{}_{}'.format(__name__, __pack_hash__, __pack_token__)

    # utility: qualify name
    def qualify(name):
        return '{}.{}'.format(base, name) if name else base

    # utility: generate resource path
    def gen_resource_path(name, is_package):
        return os.path.join(
            resource_root,
            name.replace('.', '/') + ('/__init__' if is_package else '') + '.py' +
            '-{}-{}'.format(__pack_hash__, __pack_token__),
        )

    # utility: get __all__ list from module
    def get_all_list(name):
        module = sys.modules.get(qualify(name), None)
        if module:
            all_list = getattr(module, '__all__', None)
            if all_list:
                return all_list
        return []

    # utility: __import__ wrapper
    def pack_import(name, globals=None, locals=None, fromlist=(), level=0):

        globals_ = globals if globals else {}

        # determine load path
        if level > 0:
            path = globals_.get('__package__', globals_['__name__']).split('.')
            if level > 1:
                path = path[:-(level - 1)]
        else:
            path = []
        path += name.split('.') if name else []

        # skip load requests not originating from the pack
        if globals_.get('__pack_name__', None) != __pack_name__ \
                    or globals_.get('__pack_hash__', None) != __pack_hash__ \
                    or globals_.get('__pack_token__', None) != __pack_token__:
            path = None

        # remove prefix if given
        if '.'.join(path) == base or '.'.join(path).startswith(base + '.'):
            path = path[len(base.split('.')):]

        # try to load and return module if load path is given
        if path is not None:

            # load modules along the path
            for depth in range(len(path)):
                load_module(
                    '.'.join(path[0:depth + 1]),
                    path[depth],
                    '.'.join(path[0:depth]) if depth > 0 else None,
                    True,
                )

            # load modules referenced by the from list
            if fromlist:
                for from_item in fromlist:
                    if from_item == '*':
                        all_list = get_all_list('.'.join(path) if path else None,)
                        for all_item in all_list:
                            load_module(
                                '.'.join(path + [all_item]),
                                all_item,
                                '.'.join(path) if path else None,
                                False,
                            )
                    load_module(
                        '.'.join(path + [from_item]),
                        from_item,
                        '.'.join(path) if path else None,
                        False,
                    )

            # try to return the requested module
            if not fromlist:
                request_name = qualify(path[0])
            else:
                request_name = qualify('.'.join(path))

            if request_name in sys.modules:
                return sys.modules[request_name]

        # delegate import to original routine
        return __import__(name, globals, locals, fromlist, level)

    # utility: load module from code
    def load_module(name, local, parent, override):

        # qualified names
        qualified_name = qualify(name)
        qualified_parent = qualify(parent)

        # check if module is not loaded already
        if qualified_name in sys.modules:
            return

        if not override:
            if hasattr(sys.modules[qualified_parent], local):
                return

        # check if module is available
        module_lookup = modules.get(name, None)

        if not module_lookup:
            return

        module_code, is_package = module_lookup

        # resource path
        resource_path = gen_resource_path(name, is_package)

        # create module object
        module = sys.modules[qualified_name] = imp.new_module(qualified_name)
        setattr(module, '__pack_name__', __pack_name__)
        setattr(module, '__pack_hash__', __pack_hash__)
        setattr(module, '__pack_token__', __pack_token__)
        setattr(module, '__name__', qualified_name)

        if is_package:
            setattr(module, '__package__', qualified_name)
            setattr(module, '__path__', [resource_path])
        else:
            setattr(module, '__package__', sys.modules[qualified_parent].__package__)

        # import hook for modules using __import__ the wrong way
        def pack_import_hook(name, globals=None, locals=None, fromlist=(), level=0):
            return pack_import(
                name,
                globals if globals is not None else module.__dict__,
                locals if locals is not None else module.__dict__,
                fromlist,
                level,
            )

        setattr(module, '__import__', pack_import_hook)

        # inject code
        code = compile(module_code, resource_path, 'exec')
        exec(code, module.__dict__)

        # link to parent
        setattr(sys.modules[qualified_parent], local, module)

    # import hook for modules using __import__ the wrong way
    def pack_import_hook_root(name, globals=None, locals=None, fromlist=(), level=0):
        return pack_import(
            name,
            globals if globals is not None else globals(),
            locals if locals is not None else globals(),
            fromlist,
            level,
        )

    globals()['__import__'] = pack_import_hook_root

    # support Python 3 loader system
    if sys.version_info >= (3, 0):

        # If we import this library in Python 2.x, the library can no longer be
        # imported by other modules. Weird behaviour, we would like to avoid.
        # So keep this import here!
        import importlib

        class PackLoader(importlib.abc.Loader):

            def __init__(self, name, code, is_package):
                self._name = name
                self._code = code
                self._is_package = is_package

            def create_module(self, spec):
                return None

            def exec_module(self, module):

                # resource path
                resource_path = gen_resource_path(self._name, self._is_package)

                # create module object
                setattr(module, '__pack_name__', __pack_name__)
                setattr(module, '__pack_hash__', __pack_hash__)
                setattr(module, '__pack_token__', __pack_token__)

                if self._is_package:
                    setattr(module, '__path__', [resource_path])

                # import hook for modules using __import__ the wrong way
                def pack_import_hook(name, globals=None, locals=None, fromlist=(), level=0):
                    return pack_import(
                        name,
                        globals if globals is not None else module.__dict__,
                        locals if locals is not None else module.__dict__,
                        fromlist,
                        level,
                    )

                setattr(module, '__import__', pack_import_hook)

                # inject code
                code = compile(self._code, resource_path, 'exec')
                exec(code, module.__dict__)

        class PackMetaPathFinder(importlib.abc.MetaPathFinder):

            def find_spec(self, fullname, path, target=None):

                # convert path to a list
                if not path or not hasattr(path, '__iter__'):
                    return None

                path = list(path)

                # handle only imports from the pack
                if path != list(__path__) and (
                       not len(path) > 0 \
                    or not isinstance(path[0], str) \
                    or not path[0].startswith(resource_root)
                    or not path[0].endswith('.py-{}-{}'.format(__pack_hash__, __pack_token__))
                ):
                    return None

                # construct name
                name = fullname.split('.')

                if '.'.join(name) == base or '.'.join(name).startswith(base + '.'):
                    name = name[len(base.split('.')):]

                name = '.'.join(name)

                # get module code
                module_code = modules.get(name, None)
                if not module_code:
                    return None

                # create spec
                return importlib.util.spec_from_loader(
                    qualify(name),
                    loader=PackLoader(name, module_code[0], module_code[1]),
                    is_package=True if module_code[1] else None,
                )

        sys.meta_path.insert(0, PackMetaPathFinder())


__pack_loader__()
