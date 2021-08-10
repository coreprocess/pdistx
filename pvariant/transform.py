import ast
from functools import reduce
from pathlib import Path

from pdistx.utils.source import (ast_parse, ast_unparse, read_source, write_source)


class VariantTransform(ast.NodeTransformer):

    def __init__(self, definitions):
        self.definitions = definitions
        self._collect_used_definitions = None
        super().__init__()

    # pylint: disable=pylint(invalid-name)
    def visit_Assign(self, node: ast.Assign):
        node = self.generic_visit(node)

        if len(node.targets):
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store) and target.id in self.definitions:
                return ast.Assign([target], ast.Constant(self.definitions[target.id]))

        return node

    # pylint: disable=pylint(invalid-name)
    def visit_Name(self, node: ast.Name):
        node = self.generic_visit(node)

        if isinstance(node.ctx, ast.Load) and node.id in self.definitions:
            if self._collect_used_definitions is not None:
                self._collect_used_definitions.add(node.id)
            return ast.Constant(self.definitions[node.id])

        return node

    # pylint: disable=pylint(invalid-name)
    def visit_BoolOp(self, node: ast.BoolOp):
        node = self.generic_visit(node)

        if reduce(lambda a, b: a and b, map(lambda v: isinstance(v, ast.Constant), node.values), True):
            values = map(lambda value: value.value, node.values)
            if isinstance(node.op, ast.And):
                return ast.Constant(reduce(lambda a, b: a and b, values, True))
            if isinstance(node.op, ast.Or):
                return ast.Constant(reduce(lambda a, b: a or b, values, False))

        return node

    # pylint: disable=pylint(invalid-name)
    def visit_UnaryOp(self, node: ast.UnaryOp):
        node = self.generic_visit(node)

        if isinstance(node.op, ast.Not) and isinstance(node.operand, ast.Constant):
            return ast.Constant(not node.operand.value)

        return node

    # pylint: disable=pylint(invalid-name)
    def visit_Compare(self, node: ast.Compare):
        node = self.generic_visit(node)

        if len(node.ops) == 1:
            op = node.ops[0]
            left = node.left
            right = node.comparators[0]

            if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                if isinstance(op, ast.Eq):
                    return ast.Constant(left.value == right.value)
                if isinstance(op, ast.NotEq):
                    return ast.Constant(left.value != right.value)
                if isinstance(op, ast.Lt):
                    return ast.Constant(left.value < right.value)
                if isinstance(op, ast.LtE):
                    return ast.Constant(left.value <= right.value)
                if isinstance(op, ast.Gt):
                    return ast.Constant(left.value > right.value)
                if isinstance(op, ast.GtE):
                    return ast.Constant(left.value >= right.value)
                if isinstance(op, ast.Is):
                    return ast.Constant(left.value is right.value)
                if isinstance(op, ast.IsNot):
                    return ast.Constant(left.value is not right.value)

            if isinstance(left, ast.Constant) and isinstance(right, (ast.List, ast.Tuple)):
                if reduce(lambda a, b: a and b, [isinstance(child, ast.Constant) for child in right.elts], True):
                    right_values = [child.value for child in right.elts]
                    if isinstance(op, ast.In):
                        return ast.Constant(left.value in right_values)
                    if isinstance(op, ast.NotIn):
                        return ast.Constant(left.value not in right_values)

        return node

    # pylint: disable=pylint(invalid-name)
    def visit_If(self, node: ast.If):
        node = self.generic_visit(node)

        used_definitions = self._collect_used_definitions = set()
        self._collect_used_definitions = None

        if isinstance(node.test, ast.Constant):
            if node.test.value:
                body = node.body
            else:
                body = node.orelse
            if len(body) == 0:
                body = ast.Pass()
            return body

        if len(used_definitions) > 0:
            print('line {}: {} used in if statement, but code could not be reduced'.format(
                node.lineno, ', '.join(used_definitions)))

        return node


def variant_transform(source_path: Path, target_path: Path, definitions: dict):

    # read file
    source = read_source(source_path)

    # transform
    tree = ast_parse(source)
    tree = VariantTransform(definitions).visit(tree)
    tree = ast.fix_missing_locations(tree)
    target = ast_unparse(tree)

    # write file
    write_source(target_path, target)
