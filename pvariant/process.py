import ast
from enum import Enum
from fnmatch import fnmatch
from os import listdir, makedirs
from pathlib import Path
from shutil import copyfile, rmtree
from typing import List

from .transform import VariantTransform


class IfExists(Enum):
    replace = 1
    overwrite = 2
    skip = 3

    def __str__(self):
        return str(self.name)

    @staticmethod
    def from_string(s):
        try:
            return IfExists[s]
        except KeyError:
            raise ValueError()


def perform(
    input_: Path,
    output: Path,
    if_exists: IfExists,
    ignore_patterns: List[str],
    transform_patterns: List[str],
    copy_patterns: List[str],
    definitions: dict,
):
    if True in [fnmatch(input_.name, pattern) for pattern in ignore_patterns]:
        print(f'skipping {input_}')
        return

    if output.exists():
        if if_exists == IfExists.skip and not input_.is_dir():
            return
        if if_exists == IfExists.replace and output.is_dir():
            rmtree(output)
        if if_exists == IfExists.overwrite and not input_.is_dir() and output.is_dir():
            rmtree(output)

    if input_.is_dir():
        for entry in list(listdir(input_)):
            perform(
                input_.joinpath(entry),
                output.joinpath(entry),
                if_exists,
                ignore_patterns,
                transform_patterns,
                copy_patterns,
                definitions,
            )

    elif input_.is_file():

        if True in [fnmatch(input_.name, pattern) for pattern in transform_patterns]:
            makedirs(output.parent, exist_ok=True)

            print(f'transforming {input_}')
            with open(input_, 'rt') as input_file:
                tree = ast.parse(input_file.read())
                tree = VariantTransform(definitions).visit(tree)
                with open(output, 'wt') as output_file:
                    output_file.write(ast.unparse(tree) + '\n')

        elif True in [fnmatch(input_.name, pattern) for pattern in copy_patterns]:
            makedirs(output.parent, exist_ok=True)
            print(f'copying {input_}')
            copyfile(input_, output)

        else:
            print(f'ignoring {input_}')
