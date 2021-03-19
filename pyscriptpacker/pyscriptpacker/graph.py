import os
import sys

from toposort import toposort_flatten

from .data import ImportFinder
from .file import FileQueue, FileReader


class Module(object):
    '''
    Node in a module dependency graph.
    '''

    def __init__(self, module_name, file_name):
        self.module_name = module_name
        self.file_name = file_name
        self.is_package = (file_name == '__init__.py')
        self.content = ''

    def to_dict(self):
        data = {
            'name': self.module_name,
            'is_package': self.is_package,
            'code': self.content,
        }
        return data

    def __repr__(self):
        return '<%s: %s>:\nFile: %r\nPackage: %r\nCode: %r\nImport: %r\n' % (
            self.__class__.__name__,
            self.module_name,
            self.file_name,
            self.is_package,
            self.content,
            self.imports,
        )


class ModuleGraph(object):
    '''
    Module graph tree used for detect import dependencies and order them
    if necessary.
    '''

    def __init__(self, is_compress=False):
        self._compress = is_compress

        self._queue = FileQueue()
        self._target_names = []
        self._modules = {}
        self._module_cache = {}

        self._paths = list(sys.path)

    def generate_data(self):
        '''
        Generate the dependency datas store in the module graph.

        Returns:
            list: Datas with dependency orders.
        '''
        data = []

        list_dependencies = self._build_dependency_data()
        for module in list_dependencies:
            data.append(self._modules[module].to_dict())

        return data

    def _build_dependency_data(self):
        data = {}
        for key in self._modules:
            data[key] = self._modules[key].imports

        return toposort_flatten(data)

    def parse_paths(self, paths, project_names):
        '''
        Parsing through the paths, trying to find the correct modules for
        packing based on the given arguments.

        Args:
            paths (list of string): User input library paths for finding the
                modules.
            project_names (list of string): User's main module target for
                packing.
        '''
        self._target_names = project_names
        self._paths.extend(paths)

        module_paths = []
        # Find the paths contain the desired modules.
        for module_name in project_names:
            for path in self._paths:
                full_path = os.path.join(path, module_name)
                if os.path.exists(full_path):
                    module_paths.append(full_path)
                    break

        # Find all the python file in the module paths
        for module_path in module_paths:
            for root, _, files in os.walk(module_path):
                for file in files:
                    if file.endswith('.py'):
                        self._queue.put(file, root)

        # Parsing all the files in queue
        while not self._queue.empty():
            self._parse_file(self._queue.get_file(), self._queue.get_root())

    def _parse_file(self, file_name, file_path):
        if file_path not in self._paths:
            self._paths.append(file_path)

        module_name = self._find_full_module_name(file_name, file_path)
        module = Module(module_name, file_name)

        # Get import dependencies
        import_infos = ImportFinder(file_name, file_path).list_imports
        module.imports = {
            self._find_module_of_import(info.name, info.level, file_path)
            for info in import_infos
        }
        # Remove un-supported libraries (which returned None)
        module.imports = {imp for imp in module.imports if imp is not None}

        # Read code content
        module.content = FileReader().get_file_content(
            file_name,
            file_path,
            module_name,
            self._target_names,
            self._compress,
        )

        self._modules[module_name] = module

    def _find_full_module_name(self, file_name, file_path):
        '''
        Find the full module name of the given file name by looking through its
        parent directories to see if those are also a python module.

        Args:
            file_name (string): File name to search for full module.
            file_path (string): The path which contains the given file.

        Returns:
            string: Full module name
        '''
        module_name = []

        elements = file_path.split(os.path.sep)
        while elements:
            module_name.append(elements.pop())
            # Stop when there's any python file
            contain_python = any(
                '.py' in file and file != 'setup.py'
                for file in os.listdir(os.path.sep.join(elements)))
            if not contain_python:
                break
        module_name.reverse()
        module_name = '.'.join(module_name)

        # Add file name to module name for scope management
        if '__init__.py' not in file_name:
            name = file_name.split('.py')[0]
            # Remove trailing namespace
            if os.path.sep in name:
                name = name.split(os.path.sep)[-1]
            module_name += '.' + name

        # Remove 'site-packages' path of external libraries
        if 'site-packages' in module_name:
            module_name = module_name.rpartition('site-packages.')[2]

        return module_name

    def _is_external(self, module):
        for name in self._target_names:
            if name in module:
                return False
        return True

    def _is_target(self, module):
        '''
        Check if the given module is a build target of the user.

        Returns:
            bool: Whether the module is a build target of the user.
        '''
        if '.' in module:
            module = module.split('.')[0]

        if not self._is_external(module):
            return True
        if module in sys.builtin_module_names or module in sys.modules:
            return False

        # NOTE(Nghia Lam): Not found the module name everywhere so the program
        # will try to pack it to see if this given module name is not at full
        # scope. (relative # import)
        return True

    def _find_module_of_import(self, imp_name, imp_level, file_path):
        '''
        Given a fully qualified name, find what module contains it.

        Return:
            string: Full module name of the given import information.
        '''
        if not self._is_target(imp_name):
            return None
        if imp_name.endswith('.*'):
            imp_name = imp_name[:-2]

        name = imp_name

        extrapath = None
        if imp_level and imp_level > 1:
            # NOTE(Nghia Lam): Find the trailling extra path if the level is >
            # 1 for relative import.
            # from .. import something
            # --> The path must go up one
            # from ... import something
            # --> The path must go up two
            extrapath = file_path.split(os.path.sep)
            imp_level -= 1
            extrapath = extrapath[0:-imp_level]
            extrapath = os.path.sep.join(extrapath)

        if (imp_name, extrapath) in self._module_cache:
            return self._module_cache[(imp_name, extrapath)]

        result = None
        while name:
            result = self._get_name_via_module(name, extrapath)
            if result:
                break
            result = self._get_name_via_package(name, extrapath)
            if result:
                break
            # Get everything before the last "."
            name = name.rpartition('.')[0]

            # Last fallback check when user try to import values from
            # __init__.py of root module
            if not name and imp_level and imp_level == 1:
                result = self._get_name_via_module('__init__', file_path)
                if result:
                    break

        return result

    def _get_name_via_module(self, imp_name, extrapath=None):
        imp_filename = imp_name.replace('.', os.path.sep) + '.py'

        if extrapath:
            full_path = os.path.join(extrapath, imp_filename)
            if os.path.exists(full_path):
                module_name = self._find_full_module_name(
                    imp_filename, os.path.dirname(full_path))
                if self._is_external(module_name):
                    return None
                self._module_cache[(imp_name, extrapath)] = module_name
                file = imp_filename.split(os.path.sep)[-1]
                file_path = os.path.dirname(full_path)
                if (module_name not in self._modules and
                        not self._queue.in_queue(file, file_path)):
                    self._queue.put(file, file_path)
                return module_name

        for path in self._paths:
            if not os.path.isfile(path):
                full_path = os.path.join(path, imp_filename)
                if os.path.exists(full_path):
                    module_name = self._find_full_module_name(
                        imp_filename, os.path.dirname(full_path))
                    if self._is_external(module_name):
                        return None
                    self._module_cache[(imp_name, extrapath)] = module_name
                    file = imp_filename.split(os.path.sep)[-1]
                    file_path = os.path.dirname(full_path)
                    if (module_name not in self._modules and
                            not self._queue.in_queue(file, file_path)):
                        self._queue.put(file, file_path)
                    return module_name

        return None

    def _get_name_via_package(self, imp_name, extrapath=None):
        return self._get_name_via_module(imp_name + '.__init__', extrapath)
