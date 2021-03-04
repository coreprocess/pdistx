import os
import sys
import ast


class ImportInfo(object):
    """
    A record of a name and the location of the import statement.
    """

    def __init__(self, name, filename, level):
        self.name = name
        self.filename = filename
        self.level = level

    def __repr__(self):
        # Used for debugging (print to console)
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

    def __init__(self, file_name, file_path):
        self.imports = []
        self.file_name = file_name

        with open(os.path.join(file_path, file_name)) as f:
            root = ast.parse(f.read(), file_name)
        self.visit(root)

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


class Module(object):
    """
    Node in a module dependency graph.
    """

    def __init__(self, module_name, file_name):
        self.module_name = module_name
        self.file_name = file_name
        self.is_package = False
        self.content = ''
        self.imports = []

    def to_dict(self):
        data = {
            'name': self.module_name,
            'is_package': self.is_package,
            'code': self.content,
        }
        return data

    def __repr__(self):
        # Used for debugging (print to console)
        return '<%s: %s>:\nFile: %r\nPackage: %r\nCode: %r\n' % (
            self.__class__.__name__,
            self.module_name,
            self.file_name,
            self.is_package,
            self.content,
        )


class ModuleGraph(object):
    """
    Module graph tree used for detect import dependencies and order them
    if necessary.
    """

    BUILTIN_MODULES = sys.builtin_module_names

    def __init__(self):
        self.modules = {}

    def parse_path(self, path):
        if not os.path.exists(path):
            return

        for root, _, files in os.walk(path):
            for file in files:
                # TODO(Nghia Lam): exclude `setup.py` because some structure
                # does put the `setup.py` outside of the module folder, not
                # inside it. Do we have a better way to solve this?
                if file.endswith('.py') and file != 'setup.py':
                    self.parse_file(file, root)

    def parse_file(self, file_name, file_path):
        # NOTE(Nghia Lam): We did make sure the default file_path contain at
        # least one python file, it means that the main folder in file_path is
        # a module. But we need to make get all the parent scope of the module
        # to avoid name clashes.
        module_name = self._find_module_name(file_path)
        module = Module(module_name, file_name)
        module.imports = ImportFinder(file_name, file_path).imports
        module.is_package = (file_name == '__init__.py')
        with open(os.path.join(file_path, file_name), 'r') as file_data:
            module.content = file_data.read()

        self.modules[module_name] = module

    def _find_module_name(self, file_path):
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

        return module_name
