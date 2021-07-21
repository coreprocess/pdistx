import argparse
import sys
from glob import glob
from os.path import join
from pathlib import Path
from traceback import print_tb
from typing import List

from ppack.process import perform


def main(argv: List[str] = sys.argv[1:]):

    parser = argparse.ArgumentParser(prog='ppack')

    parser.add_argument(
        '-r',
        dest='resources',
        action='store_true',
        help='create a resources folder with all non-python files (it will be named <target>_resources)',
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
        help='source package path',
    )

    parser.add_argument(
        'target',
        help='target python (will be cleared)',
    )

    args = parser.parse_args(argv)

    try:
        perform(
            Path(args.source),
            Path(args.target),
            [Path(path) for pattern in args.filter for path in glob(join(args.source, pattern), recursive=True)],
            args.resources,
            Path(args.zip) if args.zip else None,
        )
    except Exception as ex:
        print(f'ERROR: {ex}')
        print_tb(ex.__traceback__)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
