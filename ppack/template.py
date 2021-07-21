# pylint: disable=import-outside-toplevel,deprecated-module,exec-used
def __pack_loader__():

    # import all required modules
    import imp
    import os.path
    import sys
    from collections import OrderedDict

    # pack data will be injected here
    pack_mode = ''
    pack_name = ''
    pack_modules = OrderedDict()

    # verify execution model
    if __name__ == '__main__' and pack_mode != 'main':
        raise RuntimeError('pack cannot be run as main script')

    if __name__ != '__main__' and pack_mode != 'package':
        raise RuntimeError('pack can only be run as main script')

    # transform this module to a package, if necessary
    if pack_mode == 'package':
        globals()['__path__'] = []
        globals()['__package__'] = __name__

    # set resource path
    resource_root = os.path.join(
        os.path.dirname(__file__),
        os.path.splitext(__file__)[0] + '_resources',
    )

    globals()['__resource__'] = os.path.join(
        resource_root,
        '__init__.py' if pack_mode == 'package' else '__main__.py',
    )

    # determine module base
    if pack_mode == 'main':
        base = pack_name
    else:
        base = __name__

    # clear all base hoisted modules from sys.modules
    for name in list(sys.modules.keys()):
        if (pack_mode == 'main' and name == base) or name.startswith(base + '.'):
            del sys.modules[name]

    # util: unqualify name
    def unqualify_name(fullname):
        if pack_mode == 'main' and fullname == base:
            return ''
        if fullname.startswith(base + '.'):
            return fullname[len(base) + 1:]
        return None

    # util: validate name
    def validate_name(name):
        return name is not None and name in pack_modules

    def assert_name(name):
        assert validate_name(name), 'unknown module'

    # util: get __file__ for module
    def get_dunder_file(fullname):
        name = unqualify_name(fullname)
        assert_name(name)
        _, is_package = pack_modules[name]
        return os.path.join(
            __file__,
            '/'.join(name.split('.') + (['__init__.py'] if is_package else [])),
        )

    # util: get __resource__ for module
    def get_dunder_resource(fullname):
        name = unqualify_name(fullname)
        assert_name(name)
        _, is_package = pack_modules[name]
        return os.path.join(
            resource_root,
            '/'.join(name.split('.') + (['__init__.py'] if is_package else [])),
        )

    # implement pack importer
    class PackImporter:

        # check if requested module can be handled
        def find_module(self, fullname, path=None):
            name = unqualify_name(fullname)
            if validate_name(name):
                return self
            return None

        def is_package(self, fullname):
            name = unqualify_name(fullname)
            assert_name(name)
            return pack_modules[name][1]

        def get_source(self, fullname):
            name = unqualify_name(fullname)
            assert_name(name)
            return pack_modules[name][0]

        def get_code(self, fullname):
            return compile(
                self.get_source(fullname),
                get_dunder_file(fullname),
                'exec',
            )

        def load_module(self, fullname):
            code = self.get_code(fullname)
            module = sys.modules.setdefault(fullname, imp.new_module(fullname))
            module.__file__ = get_dunder_file(fullname)
            setattr(module, '__resource__', get_dunder_resource(fullname))
            module.__loader__ = self
            if self.is_package(fullname):
                module.__path__ = []
                module.__package__ = fullname
            else:
                module.__package__ = fullname.rpartition('.')[0]
            exec(code, module.__dict__)
            return module

    sys.meta_path.insert(0, PackImporter())


__pack_loader__()
