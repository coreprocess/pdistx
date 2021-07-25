import ast
from pathlib import Path
from typing import List

from pdistx.utils.source import read_source, write_source


class _ImportNameStringTransform(ast.NodeTransformer):

    def __init__(self, level, modules):
        self._level = level
        self._modules = modules
        self.uses_package_or_name = False
        self.string_rewrite_applied = False
        super().__init__()

    # pylint: disable=pylint(invalid-name)
    def visit_Name(self, node: ast.Name):
        node = self.generic_visit(node)

        if node.id in ['__package__', '__name__']:
            self.uses_package_or_name = True

        return node

    # pylint: disable=pylint(invalid-name)
    def visit_Constant(self, node: ast.Constant):
        node = self.generic_visit(node)

        if isinstance(node.value, str):
            if node.value.split('.')[0] in self._modules:
                self.string_rewrite_applied = True
                return ast.Call(
                    func=ast.Attribute(value=ast.Constant(value='.'), attr='join', ctx=ast.Load()),
                    args=[
                        ast.BinOp(
                            left=ast.Subscript(
                                value=ast.Call(
                                    func=ast.Attribute(
                                        value=ast.Name(id='__package__', ctx=ast.Load()),
                                        attr='split',
                                        ctx=ast.Load(),
                                    ),
                                    args=[ast.Constant(value='.')],
                                    keywords=[],
                                ),
                                slice=ast.Slice(upper=ast.UnaryOp(
                                    op=ast.USub(),
                                    operand=ast.Constant(value=self._level),
                                )),
                                ctx=ast.Load(),
                            ),
                            op=ast.Add(),
                            right=ast.List(elts=[node], ctx=ast.Load()),
                        )
                    ],
                    keywords=[],
                )

        return node


def _transform_import_name_string(level, modules, name):
    visitor = _ImportNameStringTransform(level, modules)
    name = visitor.visit(name)
    if visitor.uses_package_or_name or not visitor.string_rewrite_applied:
        return None
    return name


class ImportTransform(ast.NodeTransformer):

    def __init__(self, level, modules):
        self._level = level
        self._modules = modules
        super().__init__()

    # pylint: disable=pylint(invalid-name)
    def visit_Import(self, node: ast.Import):
        node = self.generic_visit(node)

        nodes = []
        for name in node.names:
            # Keep "import abc.def" and "import abc.def as xyz" for non included modules
            if name.name.split('.')[0] not in self._modules:
                nodes.append(ast.Import([name]))
                continue

            # Perform an absolute import with "__import__" to ensure nested imports are solved properly
            nodes.append(
                ast.Expr(value=ast.Call(
                    func=ast.Name(id='__import__', ctx=ast.Load()),
                    args=[
                        ast.Call(
                            func=ast.Attribute(value=ast.Constant(value='.'), attr='join', ctx=ast.Load()),
                            args=[
                                ast.BinOp(
                                    left=ast.Subscript(
                                        value=ast.Call(
                                            func=ast.Attribute(
                                                value=ast.Name(id='__package__', ctx=ast.Load()),
                                                attr='split',
                                                ctx=ast.Load(),
                                            ),
                                            args=[ast.Constant(value='.')],
                                            keywords=[],
                                        ),
                                        slice=ast.Slice(upper=ast.UnaryOp(
                                            op=ast.USub(),
                                            operand=ast.Constant(value=self._level),
                                        )),
                                        ctx=ast.Load(),
                                    ),
                                    op=ast.Add(),
                                    right=ast.List(elts=[ast.Constant(value=name.name)], ctx=ast.Load()),
                                )
                            ],
                            keywords=[],
                        ),
                        ast.Call(func=ast.Name(id='globals', ctx=ast.Load()), args=[], keywords=[]),
                        ast.Call(func=ast.Name(id='locals', ctx=ast.Load()), args=[], keywords=[]),
                        ast.List(elts=[], ctx=ast.Load()),
                        ast.Constant(value=0),
                    ],
                    keywords=[],
                )))

            # Rewrite "import abc.def" to "from .. import abc"
            if not name.asname:
                nodes.append(
                    ast.ImportFrom(
                        module=None,
                        names=[ast.alias(
                            name=name.name.split('.')[0],
                            asname=None,
                        )],
                        level=self._level + 1,
                    ))

            # Rewrite "import abc.def as xyz" to "from ..abc import def as xyz"
            else:
                nodes.append(
                    ast.ImportFrom(
                        module='.'.join(name.name.split('.')[:-1]),
                        names=[ast.alias(
                            name=name.name.split('.')[-1],
                            asname=name.asname,
                        )],
                        level=self._level + 1,
                    ))

        return nodes

    # pylint: disable=pylint(invalid-name)
    def visit_ImportFrom(self, node: ast.ImportFrom):
        node = self.generic_visit(node)

        # Rewrite "from abc import def (as xyz)" to "from ..abc import def (as xyz)"
        if node.level == 0 and node.module.split('.')[0] in self._modules:
            return ast.ImportFrom(
                module=node.module,
                names=node.names,
                level=self._level + 1,
            )

        return node

    # pylint: disable=pylint(invalid-name)
    def visit_Call(self, node: ast.Call):
        node = self.generic_visit(node)

        if isinstance(node.func, ast.Name) and isinstance(node.func.ctx, ast.Load):

            # rewrite __import__ calls
            if node.func.id == '__import__' and len(node.args) <= 5:

                # we do not support *x and **x
                has_starred = len([x for x in node.args if isinstance(x, ast.Starred)]) > 0
                has_kwargs_list = len([x for x in node.keywords if not x.arg]) > 0

                if not has_starred and not has_kwargs_list:

                    # extract arguments
                    arg_name = node.args[0] if len(node.args) > 0 else ast.Constant(value=None)
                    arg_globals = node.args[1] if len(node.args) > 1 else ast.Constant(value=None)
                    arg_locals = node.args[2] if len(node.args) > 2 else ast.Constant(value=None)
                    arg_fromlist = node.args[3] if len(node.args) > 3 else ast.List(elts=[])
                    arg_level = node.args[4] if len(node.args) > 4 else ast.Constant(value=0)

                    # extract keyword arguments
                    kwargs = {x.arg: x.value for x in node.keywords}
                    arg_name = kwargs['name'] if 'name' in kwargs else arg_name
                    arg_globals = kwargs['globals'] if 'globals' in kwargs else arg_globals
                    arg_locals = kwargs['locals'] if 'locals' in kwargs else arg_locals
                    arg_fromlist = kwargs['fromlist'] if 'fromlist' in kwargs else arg_fromlist
                    arg_level = kwargs['level'] if 'level' in kwargs else arg_level

                    # we support level 0 only
                    if isinstance(arg_level, ast.Constant) and arg_level.value == 0:

                        # transform name argument
                        arg_name = _transform_import_name_string(self._level, self._modules, arg_name)

                        # rewrite __import__ call
                        if arg_name:
                            return ast.Call(
                                func=node.func,
                                args=[arg_name, arg_globals, arg_locals, arg_fromlist, arg_level],
                                keywords=[],
                            )

            # rewrite import_module calls (importlib)
            if node.func.id == 'import_module' and len(node.args) <= 2:

                # we do not support *x and **x
                has_starred = len([x for x in node.args if isinstance(x, ast.Starred)]) > 0
                has_kwargs_list = len([x for x in node.keywords if not x.arg]) > 0

                if not has_starred and not has_kwargs_list:

                    # extract arguments
                    arg_name = node.args[0] if len(node.args) > 0 else ast.Constant(value=None)
                    arg_package = node.args[1] if len(node.args) > 1 else ast.Constant(value=None)

                    # extract keyword arguments
                    kwargs = {x.arg: x.value for x in node.keywords}
                    arg_name = kwargs['name'] if 'name' in kwargs else arg_name
                    arg_package = kwargs['package'] if 'package' in kwargs else arg_package

                    # transform name argument
                    arg_name = _transform_import_name_string(self._level, self._modules, arg_name)

                    # rewrite __import__ call
                    if arg_name:
                        return ast.Call(
                            func=node.func,
                            args=[arg_name, arg_package],
                            keywords=[],
                        )

        return node


def import_transform(source_path: Path, target_path: Path, level: int, modules: List[str]):

    # read file
    source = read_source(source_path)

    # transform
    tree = ast.parse(source, filename=str(source_path), type_comments=True)
    tree = ImportTransform(level, modules).visit(tree)
    tree = ast.fix_missing_locations(tree)
    target = ast.unparse(tree)

    # write file
    write_source(target_path, target)
