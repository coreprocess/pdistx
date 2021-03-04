import os
import sys
import ast

from pyscriptpacker import utils
from pyscriptpacker import graph


class ImportInfo(object):
    """A record of a name and the location of the import statement."""

    def __init__(self, name, filename, level):
        self.name = name
        self.filename = filename
        self.level = level

    def __repr__(self):
        return '%s(%r, %r, %r)' % (
            self.__class__.__name__,
            self.name,
            self.filename,
            self.level,
        )


class ImportFinder(ast.NodeVisitor):
    """
    This class is implemented as a NodeVisitor which will collect all the
    import dependencies when visit a new file as root.

    Reference: https://www.mattlayman.com/blog/2018/decipher-python-ast/
    """

    def __init__(self, file_name):
        self.imports = []
        self.file_name = file_name

    def visit_Import(self, node):
        for alias in node.names:
            self._process(alias.name, None)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            fullname = '%s.%s' % (node.module,
                                  alias.name) if node.module else alias.name
            self._process(fullname, node.level)

    def _process(self, full_name, level):
        info = ImportInfo(full_name, self.file_name, level)
        self.imports.append(info)


def find_imports(file_name, file_path):
    with open(os.path.join(file_path, file_name)) as f:
        root = ast.parse(f.read(), file_name)
    visitor = ImportFinder(file_name)
    visitor.visit(root)
    return visitor.imports


def find_all_module_paths(library_paths):
    all_module_paths = []

    for lib_path in library_paths:
        if not os.path.exists(lib_path):
            continue

        for root, _, files in os.walk(lib_path):
            is_module = False
            for file in files:
                # TODO(Nghia Lam): exclude `setup.py` because some structure
                # does put the `setup.py` outside of the module folder, not
                # inside it. Do we have a better way to solve this?
                if '.py' in file and file != 'setup.py':
                    is_module = True
                    break
            if is_module and root not in all_module_paths:
                all_module_paths.append(root)

    return all_module_paths


def write_output(output_path, texts):
    try:
        with open(output_path, 'w') as output:
            # TODO(Nghia Lam): Something wrong with new line characters '\n',
            # it cannot write a new line ...
            output.write(texts)
    except IOError as e:
        sys.stdout.write('Error: Cannot write to ' + output_path +
                         '\nPlease make sure the directory is valid!!\n' +
                         str(e))
        sys.exit(1)


def get_setup_module_code(python_version):
    return (utils.py2_setup_code
            if python_version == '2.7' else utils.py3_setup_code)


def pack_modules(product_name, library_paths):
    modules = []

    # Add product base modules
    module_paths = find_all_module_paths(library_paths)
    for path in module_paths:
        for root, _, files in os.walk(path):
            for file in files:
                # Open file for reading
                find_imports(file, root)
                with open(os.path.join(root, file), 'r') as file_data:
                    file_text = file_data.read()

                # Add to modules
                folder_name = os.path.basename(os.path.normpath(root))
                file_name = file.split('.py')[0]
                module_item = {
                    'name': (
                        ('.'.join([product_name, folder_name]))
                        if file == '__init__.py' else
                        ('.'.join([product_name, folder_name, file_name]))),
                    'is_package': file == '__init__.py',
                    'code': str(file_text),
                }
                modules.append(module_item)

    return modules


def pack(python_version, output_path, product_name, library_paths):
    main_script = 'import sys\n'

    # Add modules to main_script
    modules = pack_modules(product_name, library_paths)
    main_script += ('_modules = [' +
                    ','.join([str(module) for module in modules]) + ']')

    # Setup module code
    main_script += get_setup_module_code(python_version)

    module_graph = graph.ModuleGraph()

    write_output(output_path, main_script)
