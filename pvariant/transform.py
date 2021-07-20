import ast
from functools import reduce
from pathlib import Path


class VariantTransform(ast.NodeTransformer):

    def __init__(self, definitions):
        self.definitions = definitions
        self._collect_used_definitions = None
        super().__init__()

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets):
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store) and target.id in self.definitions:
                return ast.copy_location(
                    ast.Assign([target], ast.Constant(self.definitions[target.id])),
                    node,
                )
        return node

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id in self.definitions:
            if self._collect_used_definitions is not None:
                self._collect_used_definitions.add(node.id)
            return ast.copy_location(
                ast.Constant(self.definitions[node.id]),
                node,
            )
        return node

    def visit_BoolOp(self, node: ast.BoolOp):
        values = [self.visit(child) for child in node.values]
        if reduce(lambda a, b: a and b, map(lambda v: isinstance(v, ast.Constant), values), True):
            real_values = map(lambda value: value.value, values)
            if isinstance(node.op, ast.And):
                return ast.copy_location(
                    ast.Constant(reduce(lambda a, b: a and b, real_values, True)),
                    node,
                )
            if isinstance(node.op, ast.Or):
                return ast.copy_location(
                    ast.Constant(reduce(lambda a, b: a or b, real_values, False)),
                    node,
                )
        return node

    def visit_UnaryOp(self, node: ast.UnaryOp):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.Not) and isinstance(operand, ast.Constant):
            return ast.copy_location(
                ast.Constant(not operand.value),
                node,
            )
        return node

    def visit_Compare(self, node: ast.Compare):
        if len(node.ops) == 1:
            op = node.ops[0]
            left = self.visit(node.left)
            right = self.visit(node.comparators[0])
            if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                if isinstance(op, ast.Eq):
                    return ast.copy_location(
                        ast.Constant(left.value == right.value),
                        node,
                    )
                if isinstance(op, ast.NotEq):
                    return ast.copy_location(
                        ast.Constant(left.value != right.value),
                        node,
                    )
                if isinstance(op, ast.Lt):
                    return ast.copy_location(
                        ast.Constant(left.value < right.value),
                        node,
                    )
                if isinstance(op, ast.LtE):
                    return ast.copy_location(
                        ast.Constant(left.value <= right.value),
                        node,
                    )
                if isinstance(op, ast.Gt):
                    return ast.copy_location(
                        ast.Constant(left.value > right.value),
                        node,
                    )
                if isinstance(op, ast.GtE):
                    return ast.copy_location(
                        ast.Constant(left.value >= right.value),
                        node,
                    )
                if isinstance(op, ast.Is):
                    return ast.copy_location(
                        ast.Constant(left.value is right.value),
                        node,
                    )
                if isinstance(op, ast.IsNot):
                    return ast.copy_location(
                        ast.Constant(left.value is not right.value),
                        node,
                    )
            if isinstance(left, ast.Constant) and (isinstance(right, ast.List) or isinstance(right, ast.Tuple)):
                if reduce(lambda a, b: a and b, [isinstance(child, ast.Constant) for child in right.elts], True):
                    right_values = [child.value for child in right.elts]
                    if isinstance(op, ast.In):
                        return ast.copy_location(
                            ast.Constant(left.value in right_values),
                            node,
                        )
                    if isinstance(op, ast.NotIn):
                        return ast.copy_location(
                            ast.Constant(left.value not in right_values),
                            node,
                        )
        return node

    def visit_If(self, node: ast.If):
        used_definitions = self._collect_used_definitions = set()
        test = self.visit(node.test)
        self._collect_used_definitions = None

        if isinstance(test, ast.Constant):
            if test.value:
                body = [self.visit(child) for child in node.body]
            else:
                body = [self.visit(child) for child in node.orelse]
            if len(body) == 0:
                body = [ast.copy_location(ast.Pass(), node)]
            return body

        if len(used_definitions) > 0:
            print('line {}: {} used in if statement, but code could not be reduced'.format(
                node.lineno, ', '.join(used_definitions)))

        return node


def variant_transform(source_path: Path, target_path: Path, definitions: dict):
    # read file
    with open(source_path, 'r') as sf:
        source = sf.read()

    # transform
    tree = ast.parse(source, filename=str(source_path), type_comments=True)
    tree = VariantTransform(definitions).visit(tree)
    tree = ast.fix_missing_locations(tree)
    target = ast.unparse(tree)

    # write file
    with open(target_path, 'w') as tf:
        tf.write(target)
