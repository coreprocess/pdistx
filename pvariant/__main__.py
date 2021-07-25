import sys

# avoid having the cwd in the path
# see https://docs.python.org/3/tutorial/modules.html#the-module-search-path
if '' in sys.path:
    sys.path.remove('')

import argparse
from glob import glob
from os.path import join
from pathlib import Path
from traceback import print_tb
from typing import List

from pvariant.process import perform


def main(argv: List[str] = sys.argv[1:]):

    parser = argparse.ArgumentParser(prog='pvariant')

    parser.add_argument(
        '-d',
        dest='define',
        metavar='name[:type]=value',
        action='append',
        default=[],
        help='define variables to be replaced, e.g. -d __VARIANT__=PRO -d __LICENSE_CHECK__:bool=True',
    )

    parser.add_argument(
        '-f',
        dest='filter',
        metavar='filter',
        action='append',
        default=[],
        help='defines files and folders to be filtered out (glob pattern)',
    )

    parser.add_argument(
        '-z',
        dest='zip',
        metavar='zip',
        default=None,
        help='zip file path (target becomes relative path within zip file)',
    )

    parser.add_argument(
        'source',
        help='source path',
    )

    parser.add_argument(
        'target',
        help='target path (will be cleared)',
    )

    args = parser.parse_args(argv)

    definitions = {}

    for def_ in args.define:
        name, value = [*def_.split('=', 2), None][0:2]
        name, type_ = [*name.split(':', 2), 'str'][0:2]
        type_ = type_.lower()
        if type_ in ['', 'str']:
            value = value if value is not None else ''
        elif type_ == 'int':
            value = int(value if value is not None else 0)
        elif type_ == 'bool':
            value = value is not None and value.lower() == 'true'
        elif type_ == 'none':
            value = None
        else:
            raise ValueError('invalid definition type')
        if name:
            definitions[name] = value

    try:
        perform(
            Path(args.source),
            Path(args.target),
            definitions,
            [Path(path) for pattern in args.filter for path in glob(join(args.source, pattern), recursive=True)],
            Path(args.zip) if args.zip else None,
        )
    except Exception as ex:
        print(f'ERROR: {ex}')
        print_tb(ex.__traceback__)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
