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
        action='store_true',
        help='provide target as zip file',
    )

    parser.add_argument(
        'target',
        help='target folder or zip file (will be cleared, except for the ones to be kept)',
    )

    args = parser.parse_args()

    perform(
        [Path(req).absolute() for req in args.requirements],
        args.pip,
        [Path(req).absolute() for req in args.source],
        Path(args.target).absolute(),
        args.keep if args.keep else ['requirements.txt', '.gitignore'],
        args.zip,
    )


if __name__ == '__main__':
    main()
