import ast
from pathlib import Path


class ImportTransform(ast.NodeTransformer):

    def __init__(self, level):
        self._level = level
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
                                        args=[
                                            ast.Constant(
                                                value='.',
                                                kind=None,
                                            )
                                        ],
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
                        names=[
                            ast.alias(
                                name=name.name.split('.')[0],
                                asname=None,
                            )
                        ],
                        level=self._level,
                    ))

            else:
                nodes.append(
                    ast.ImportFrom(
                        module='.'.join(name.name.split('.')[:-1]),
                        names=[
                            ast.alias(
                                name=name.name.split('.')[-1],
                                asname=name.asname,
                            )
                        ],
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


with open(Path(__file__).parent.joinpath('test2.py').resolve()) as f:
    tree = ast.parse(f.read())
    tree = ast.fix_missing_locations(ImportTransform(2).visit(tree))
    print(ast.unparse(tree))
