import ast
from pathlib import Path
from typing import List


class ImportTransform(ast.NodeTransformer):

    def __init__(self, level, modules):
        self._level = level
        self._modules = modules
        super().__init__()

    def visit_Import(self, node: ast.Import):
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

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # Rewrite "from abc import def (as xyz)" to "from ..abc import def (as xyz)"
        if node.level == 0 and node.module.split('.')[0] in self._modules:
            return ast.ImportFrom(
                module=node.module,
                names=node.names,
                level=self._level + 1,
            )

        return node


def import_transform(source_path: Path, target_path: Path, level: int, modules: List[str]):
    # read file
    with open(source_path, 'r') as sf:
        source = sf.read()

    # transform
    tree = ast.parse(source, filename=str(source_path), type_comments=True)
    tree = ImportTransform(level, modules).visit(tree)
    tree = ast.fix_missing_locations(tree)
    target = ast.unparse(tree)

    # write file
    with open(target_path, 'w') as tf:
        tf.write(target)
