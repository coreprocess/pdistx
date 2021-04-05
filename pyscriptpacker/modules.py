import os
import logging

from .files import get_file_content
from .compression import compress_source, minify_source


class ModuleInfo(object):
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


class ModuleManager(object):
    '''
    Module manager for manage all the module found while parsing through the
    required paths.
    '''

    def __init__(self, compress, minify, extra_path=None):
        self._compress = compress
        self._minify = minify

        self._modules = dict()
        self._paths = []
        if extra_path:
            self._paths.append(extra_path)

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

    def process_file_content(self, file):
        content = get_file_content(file)
        if self._minify:
            content = minify_source(content)
        if self._compress:
            content = compress_source(content)
        return content

    def parse_paths(self, paths, module_names):
        '''
        Parsing through the paths, trying to find the correct modules for
        packing based on the given arguments.

        Args:
            paths (list of string): User input library paths for finding the
                modules.
            module_names (list of string): User's main module target for
                packing.
        '''
        self._paths.extend(paths)

        # Find the paths contain the desired modules.
        for module_name in module_names:
            found = False
            for path in self._paths:
                full_path = os.path.join(path, module_name)
                if os.path.exists(full_path):
                    # Find all the python file in the module paths
                    for file_path, _, files in os.walk(full_path):
                        for file in files:
                            if file.endswith('.py'):
                                self._parse_file(file, file_path, path)
                    found = True
                    break

                # Fallback for single file library like 'toposort'
                full_path_file = full_path + '.py'
                if os.path.exists(full_path_file):
                    self._parse_file(
                        os.path.basename(full_path_file),
                        os.path.dirname(full_path_file),
                        path,
                    )
                    found = True
                    break
            if not found:
                logging.error('Cannot find module for packing: %s', module_name)

    def _parse_file(self, file_name, file_path, root):
        full_module_name = self._find_module_of_file(file_name, file_path, root)
        module = ModuleInfo(full_module_name, file_name)

        # Read code content
        module.content = self.process_file_content(
            os.path.join(file_path, file_name))

        self._modules[full_module_name] = module

    def _find_module_of_file(self, file_name, file_path, root):
        '''
        Find the full module name of the given file name.

        Args:
            file_name (string): File name to search for full module.
            file_path (string): The path which contains the given file.
            root (string): The root path user input.

        Returns:
            string: Full module name
        '''
        module_name = os.path.relpath(file_path, root)
        module_name = module_name.replace(os.path.sep, '.')
        module_name = None if module_name == '.' else module_name

        # Add file name to module name for scope management
        if '__init__.py' not in file_name:
            name = file_name.split('.py')[0]
            # Remove trailing namespace
            if os.path.sep in name:
                name = name.split(os.path.sep)[-1]
            module_name = '.'.join([module_name, name]) if module_name else name

        return module_name
