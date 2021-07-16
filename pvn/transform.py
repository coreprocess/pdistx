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
            nodes.append(
                ast.Expr(value=ast.Call(
                    func=ast.Name(id='__import__', ctx=ast.Load()),
                    args=[
                        ast.BinOp(
                            left=ast.BinOp(
                                left=ast.Subscript(
                                    value=ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(
                                                id='__package__',
                                                ctx=ast.Load(),
                                            ),
                                            attr='split',
                                            ctx=ast.Load(),
                                        ),
                                        args=[ast.Constant(
                                            value='.',
                                            kind=None,
                                        )],
                                        keywords=[],
                                    ),
                                    slice=ast.Slice(
                                        lower=None,
                                        upper=ast.UnaryOp(
                                            op=ast.USub(),
                                            operand=ast.Constant(
                                                value=self._level,
                                                kind=None,
                                            ),
                                        ),
                                        step=None,
                                    ),
                                    ctx=ast.Load(),
                                ),
                                op=ast.Add(),
                                right=ast.Constant(value='.', kind=None),
                            ),
                            op=ast.Add(),
                            right=ast.Constant(value=name.name, kind=None),
                        ),
                        ast.Call(
                            func=ast.Name(id='globals', ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                        ast.Call(
                            func=ast.Name(id='locals', ctx=ast.Load()),
                            args=[],
                            keywords=[],
                        ),
                        ast.List(elts=[], ctx=ast.Load()),
                        ast.Constant(value=0, kind=None),
                    ],
                    keywords=[],
                )))

            if not name.asname:
                nodes.append(
                    ast.ImportFrom(
                        module=None,
                        names=[ast.alias(
                            name=name.name.split('.')[0],
                            asname=None,
                        )],
                        level=self._level,
                    ))

            else:
                nodes.append(
                    ast.ImportFrom(
                        module='.'.join(name.name.split('.')[:-1]),
                        names=[ast.alias(
                            name=name.name.split('.')[-1],
                            asname=name.asname,
                        )],
                        level=self._level,
                    ))

        return nodes

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.level == 0:
            return ast.ImportFrom(
                module=node.module,
                names=node.names,
                level=self._level,
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
