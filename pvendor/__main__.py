import argparse
from pathlib import Path

from pvendor.process import perform


def main():
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
        help='pip command',
    )

    parser.add_argument(
        'target',
        help='target folder'
        ' (will be cleared, except for an existing requirements.txt)',
    )

    args = parser.parse_args()

    perform(
        [Path(req).absolute() for req in args.requirements],
        [Path(req).absolute() for req in args.source],
        Path(args.target).absolute(),
        args.pip,
    )


if __name__ == '__main__':
    main()
