import os
import sys
import bz2
import base64


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

    def __init__(self, is_compress=False):
        self._compress = is_compress
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
        module_paths = []
        # Find the paths contain the desired modules.
        for module_name in project_names:
            for path in paths:
                full_path = os.path.join(path, module_name)
                if os.path.exists(full_path):
                    module_paths.append(full_path)
                    break
                # Fallback for single file library like 'toposort'
                full_path_file += '.py'
                if os.path.exists(full_path_file):
                    module_paths.append(full_path)
                    break

        # Find all the python file in the module paths
        for module_path in module_paths:
            for root, _, files in os.walk(module_path):
                for file in files:
                    if file.endswith('.py'):
                        self._parse_file(file, root)

    def _parse_file(self, file_name, file_path):
        module_name = self._find_module_of_file(file_name, file_path)
        module = ModuleInfo(module_name, file_name)

        # Read code content
        module.content = self._get_file_content(
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

    def _get_file_content(self, file_name, file_path, compress=True):
        '''
        Get the content of given file with options for compressing the source.

        Args:
            file_name (string): The file for getting the content.
            file_path (string): The path to the file.
            compress (bool, optional): Whether the source will be compressed
                using bz2. Defaults to True.

        Returns:
            string: The whole content of the given file.
        '''
        content = ''
        with open(os.path.join(file_path, file_name), 'r') as file_data:
            content = file_data.read()

            if compress:
                # Reference: https://github.com/liftoff/pyminifier/blob/087ea7b0c8c964f1f907c3f350f5ce281798db86/pyminifier/compression.py#L51-L76
                compressed_source = bz2.compress(content.encode('utf-8'))
                content = 'import bz2, base64\n'
                content += 'exec(bz2.decompress(base64.b64decode("'
                content += base64.b64encode(compressed_source).decode('utf-8')
                content += '")))\n'
        return content
