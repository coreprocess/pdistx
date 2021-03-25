import os
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
        self._modules = dict()

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
        # Find the paths contain the desired modules.
        for module_name in module_names:
            for path in paths:
                full_path = os.path.join(path, module_name)
                if os.path.exists(full_path):
                    # Find all the python file in the module paths
                    for file_path, _, files in os.walk(full_path):
                        for file in files:
                            if file.endswith('.py'):
                                self._parse_file(file, file_path, path)
                    break

                # Fallback for single file library like 'toposort'
                full_path_file = full_path + '.py'
                if os.path.exists(full_path_file):
                    self._parse_file(
                        os.path.basename(full_path_file),
                        os.path.dirname(full_path_file),
                        path,
                    )

    def _parse_file(self, file_name, file_path, root):
        full_module_name = self._find_module_of_file(file_name, file_path, root)
        module = ModuleInfo(full_module_name, file_name)

        # Read code content
        module.content = self._get_file_content(
            file_name,
            file_path,
            self._compress,
        )

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
