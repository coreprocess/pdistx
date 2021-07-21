# pylint: disable=import-outside-toplevel,deprecated-module,exec-used
def __pack_loader__():

    # import all required modules
    import imp
    import sys
    from collections import OrderedDict

    # pack data will be injected here
    pack_mode = ''
    pack_name = ''
    pack_hash = ''
    pack_modules = {}

    # verify execution model
    if __name__ == '__main__' and pack_mode != 'main':
        raise RuntimeError('pack cannot be run as main script')

    if __name__ != '__main__' and pack_mode != 'package':
        raise RuntimeError('pack can only be run as main script')

    # transform this module to a package, if necessary
    if pack_mode == 'package':
        globals()['__path__'] = []
        globals()['__package__'] = __name__

    # determine module base
    if pack_mode == 'main':
        base = '{}_{}'.format(pack_name, pack_hash)
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

    # implement pack importer
    class PackImporter:

        # check if requested module can be handled
        def find_module(self, fullname, path=None):
            name = unqualify_name(fullname)
            if name is not None and name in pack_modules:
                return self
            return None

        def is_package(self, fullname):
            name = unqualify_name(fullname)
            assert name is not None and name in pack_modules, 'unknown module'
            return pack_modules[name][1]

        def get_source(self, fullname):
            name = unqualify_name(fullname)
            assert name is not None and name in pack_modules, 'unknown module'
            return pack_modules[name][0]

        def get_code(self, fullname):
            return compile(self.get_source(fullname), __file__, 'exec')

        def load_module(self, fullname):
            code = self.get_code(fullname)
            module = sys.modules.setdefault(fullname, imp.new_module(fullname))
            module.__file__ = __file__
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
