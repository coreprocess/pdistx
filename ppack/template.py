__pack_mode__ = ''
__pack_module__ = ''
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
    from collections import OrderedDict

    # generate token
    global __pack_token__
    __pack_token__ = binascii.hexlify(os.urandom(4)).decode('utf-8')

    # modules will be injected here
    modules = {}

    # determine resource root
    resource_root = os.path.splitext(__file__)[0] + '_resources'

    # determine module base
    if __name__ == '__main__':
        base = __pack_module__
    else:
        base = __name__

    # construct base module
    if __name__ == '__main__':
        sys.modules[base] = imp.new_module(base)
        setattr(sys.modules[base], '__name__', base)
        setattr(sys.modules[base], '__package__', base)
        setattr(sys.modules[base], '__path__', [])

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

        print('pack_import name={}'.format(name))

        globals_ = globals if globals else {}

        # determine load name
        if level > 0:
            load = globals_.get('__package__', globals_['__name__']).split('.')
            if level > 1:
                load = load[:-(level - 1)]
        else:
            load = []
        load += name.split('.') if name else []

        # return base module
        if '.'.join(load) == base:
            return sys.modules[base]

        # remove prefix if given
        if '.'.join(load).startswith(base + '.'):
            load = load[len(base.split('.')):]

        # replace prefix if necessary
        if '.'.join(load) == __name__:
            load = __pack_module__.split('.')
        elif '.'.join(load).startswith(__name__ + '.'):
            load = __pack_module__.split('.') + load[len(__name__.split('.')):]

        # return this module
        if __pack_mode__ == 'module' and '.'.join(load) == __pack_module__:
            return sys.modules[__name__]

        # load modules along the path
        for depth in range(len(load)):
            load_module('.'.join(load[0:depth + 1]), True)

        # load modules referenced by the from list
        if fromlist:
            for from_item in fromlist:
                if from_item == '*':
                    all_list = get_all_list('.'.join(load) if load else None)
                    for all_item in all_list:
                        load_module('.'.join(load + [all_item]), False)
                load_module('.'.join(load + [from_item]), False)

        # try to return the requested module
        if not fromlist:
            request = qualify(load[0])
        else:
            request = qualify('.'.join(load))

        if request in sys.modules:
            return sys.modules[request]

        # fallback to original import
        return __import__(name, globals, locals, fromlist, level)

    # utility: load module from code
    def load_module(name, override):

        # get local and parent name
        local = name.split('.')[-1]
        parent = '.'.join(name.split('.')[:-1])
        if not parent:
            parent = None

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
        code, is_package = modules.get(name, (None, None))

        if code is None:
            return

        # resource path
        resource_path = gen_resource_path(name, is_package)

        # create module object
        print('pack(__import__): loading {} as {}', name, qualified_name)

        module = sys.modules[qualified_name] = imp.new_module(qualified_name)
        setattr(module, '__pack_module__', __pack_module__)
        setattr(module, '__pack_hash__', __pack_hash__)
        setattr(module, '__pack_token__', __pack_token__)
        setattr(module, '__name__', qualified_name)

        if is_package:
            setattr(module, '__package__', qualified_name)
            setattr(module, '__path__', [resource_path])
        else:
            setattr(module, '__package__', qualified_parent)

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

        # load module code
        try:
            code = compile(code, resource_path, 'exec')
            exec(code, module.__dict__)

        except:
            # remove module in case load failed
            del sys.modules[qualified_name]

        else:
            # link to parent in case load succeeded
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

    setattr(sys.modules[__name__], '__import__', pack_import_hook_root)

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
                setattr(module, '__pack_module__', __pack_module__)
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

                print('find_spec fullname={}'.format(fullname))

                # convert path to a list
                if not path or not hasattr(path, '__iter__'):
                    return None

                path = list(path)
                print(path)
                print(__file__)

                # handle only imports from the pack
                # from_this = (
                #         len(path) > 0 \
                #     and isinstance(path[0], str) \
                #     and path[0] == __file__
                # )
                # from_pack = (
                #         len(path) > 0 \
                #     and isinstance(path[0], str) \
                #     and path[0].startswith(resource_root) \
                #     and path[0].endswith('.py-{}-{}'.format(__pack_hash__, __pack_token__))
                # )

                # print(str(from_this))
                # print(str(from_pack))

                # if not from_this and not from_pack:
                #     return None

                # the base cannot be loaded
                if fullname == base:
                    return None

                # remove prefix if given
                if fullname.startswith(base + '.'):
                    load = fullname[len(base) + 1:]
                else:
                    load = fullname

                # replace prefix if necessary
                if load == __name__:
                    load = __pack_module__
                elif load.startswith(__name__ + '.'):
                    load = __pack_module__ + load[len(__name__):]

                # this module cannot be loaded
                if __pack_mode__ == 'module' and load == __pack_module__:
                    return None

                # get module code
                code, is_package = modules.get(load, (None, None))
                if code is None:
                    return None

                # create spec
                print('pack(importlib): loading {} as {}', load, fullname)

                return importlib.util.spec_from_loader(
                    qualify(load),
                    loader=PackLoader(load, code, is_package),
                    is_package=True if is_package else None,
                )

        sys.meta_path.insert(0, PackMetaPathFinder())


__pack_loader__()
