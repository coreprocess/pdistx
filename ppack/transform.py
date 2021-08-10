import ast

from pdistx.utils.source import ast_parse, ast_unparse


class FileToResourceTransform(ast.NodeTransformer):

    # pylint: disable=pylint(invalid-name)
    def visit_Name(self, node: ast.Name):
        node = self.generic_visit(node)

        if isinstance(node.ctx, ast.Load) and node.id == '__file__':
            return ast.Name('__resource__', ast.Load())

        return node


def file_to_resource_transform(source: str):
    tree = ast_parse(source)
    tree = FileToResourceTransform().visit(tree)
    tree = ast.fix_missing_locations(tree)
    return ast_unparse(tree)
