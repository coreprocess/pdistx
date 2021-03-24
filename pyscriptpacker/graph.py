import os
import sys

from .file import FileHandler


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
        return '<%s: %s>:\nFile: %r\nPackage: %r\nCode: %r\n' % (
            self.__class__.__name__,
            self.module_name,
            self.file_name,
            self.is_package,
            self.content,
        )


class ModuleGraph(object):
    '''
    Module graph tree used for detect import dependencies and order them
    if necessary.
    '''

    def __init__(self, is_compress=False):
        self._compress = is_compress

        self._paths = list(sys.path)
        self._modules = {}

    def generate_data(self):
        '''
        Generate the dependency datas store in the module graph.

        Returns:
            list: Datas with dependency orders.
        '''
        data = []

        for module in self._modules:
            data.append(self._modules[module].to_dict())

        return data

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
                        self._parse_file(file, root)

    def _parse_file(self, file_name, file_path):
        if file_path not in self._paths:
            self._paths.append(file_path)

        module_name = self._find_module_of_file(file_name, file_path)
        module = Module(module_name, file_name)

        # Read code content
        module.content = FileHandler.get_file_content(
            file_name,
            file_path,
            self._compress,
        )

        self._modules[module_name] = module

    def _find_module_of_file(self, file_name, file_path):
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
