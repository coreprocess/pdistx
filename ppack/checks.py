import ast

from pdistx.utils.source import ast_parse


class _HasAbsoluteImportOfModuleCheck(ast.NodeVisitor):

    def __init__(self, module):
        self._module = module
        self.has_absolute_import_of_module = False
        super().__init__()

    # pylint: disable=pylint(invalid-name)
    def visit_Import(self, node: ast.Import):
        self.generic_visit(node)

        for name in node.names:
            if name.name == self._module or name.name.startswith(self._module + '.'):
                self.has_absolute_import_of_module = True

    # pylint: disable=pylint(invalid-name)
    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.generic_visit(node)

        if node.level == 0:
            if node.module == self._module or node.module.startswith(self._module + '.'):
                self.has_absolute_import_of_module = True


def has_absolute_import_of_module(source, module):
    visitor = _HasAbsoluteImportOfModuleCheck(module)
    visitor.visit(ast_parse(source))
    return visitor.has_absolute_import_of_module


class _HasRelativeImportCheck(ast.NodeVisitor):

    def __init__(self):
        self.has_relative_import = False
        super().__init__()

    # pylint: disable=pylint(invalid-name)
    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.generic_visit(node)

        if node.level != 0:
            self.has_relative_import = True


def has_relative_import(source):
    visitor = _HasRelativeImportCheck()
    visitor.visit(ast_parse(source))
    return visitor.has_relative_import
