import sys

# avoid having the cwd in the path
# see https://docs.python.org/3/tutorial/modules.html#the-module-search-path
if '' in sys.path:
    sys.path.remove('')

import argparse
from pathlib import Path
from traceback import print_tb
from typing import List

from pvendor.process import perform


def main(argv: List[str] = sys.argv[1:]):

    parser = argparse.ArgumentParser(prog='pvendor')

    parser.add_argument(
        '-r',
        dest='requirements',
        metavar='requirements',
        action='append',
        default=[],
        help='install packages from requirements.txt',
    )

    parser.add_argument(
        '-s',
        dest='source',
        metavar='source',
        action='append',
        default=[],
        help='copy modules from source folder',
    )

    parser.add_argument(
        '-p',
        dest='pip',
        metavar='pip',
        default='pip',
        help='pip command (defaults to pip)',
    )

    parser.add_argument(
        '-k',
        dest='keep',
        metavar='keep',
        action='append',
        default=[],
        help='files or folders to be kept in the target folder (defaults to requirements.txt and .gitignore)',
    )

    parser.add_argument(
        '-z',
        dest='zip',
        metavar='zip',
        default=None,
        help='zip file path (target becomes relative path within zip file)',
    )

    parser.add_argument(
        'target',
        help='target folder (will be cleared, except for the ones to be kept)',
    )

    args = parser.parse_args(argv)

    try:
        perform(
            [Path(req) for req in args.requirements],
            args.pip,
            [Path(req) for req in args.source],
            Path(args.target),
            args.keep if args.keep else ['requirements.txt', '.gitignore'],
            Path(args.zip) if args.zip else None,
        )
    except Exception as ex:
        print(f'ERROR: {ex}')
        print_tb(ex.__traceback__)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
