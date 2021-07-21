import ast


class FileToResourceTransform(ast.NodeTransformer):

    def __init__(self):
        super().__init__()

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id == '__file__':
            return ast.copy_location(
                ast.Name('__resource__', ast.Load()),
                node,
            )
        return node


def file_to_resource_transform(source: str):
    tree = ast.parse(source, type_comments=True)
    tree = FileToResourceTransform().visit(tree)
    tree = ast.fix_missing_locations(tree)
    return ast.unparse(tree)
