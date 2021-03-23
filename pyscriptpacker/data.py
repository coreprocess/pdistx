import os
import ast


class ImportInfo(object):
    '''
    A record of a name and the location of the import statement.
    '''

    def __init__(self, name, level):
        self.name = name
        self.level = level

    def __repr__(self):
        return '%s(%r, %r)' % (
            self.__class__.__name__,
            self.name,
            self.level,
        )


class ImportFinder(ast.NodeVisitor):
    '''
    This class is implemented as a NodeVisitor which will collect all the
    import dependencies when visit a new file as root.

    Reference: https://www.mattlayman.com/blog/2018/decipher-python-ast/
    '''

    def __init__(self, file_name, file_path):
        self._imports = []

        with open(os.path.join(file_path, file_name)) as f:
            root = ast.parse(f.read(), file_name)
        self.visit(root)

    @property
    def list_imports(self):
        return self._imports

    def visit_Import(self, node):
        for alias in node.names:
            self._process(alias.name, None)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            fullname = '%s.%s' % (node.module,
                                  alias.name) if node.module else alias.name
            self._process(fullname, node.level)

    def _process(self, full_name, level):
        info = ImportInfo(full_name, level)
        self._imports.append(info)
