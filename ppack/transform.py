import ast


class FileToResourceTransform(ast.NodeTransformer):

    # pylint: disable=pylint(invalid-name)
    def visit_Name(self, node: ast.Name):
        node = self.generic_visit(node)

        if isinstance(node.ctx, ast.Load) and node.id == '__file__':
            return ast.Name('__resource__', ast.Load())

        return node


def file_to_resource_transform(source: str):
    tree = ast.parse(source, type_comments=True)
    tree = FileToResourceTransform().visit(tree)
    tree = ast.fix_missing_locations(tree)
    return ast.unparse(tree)
