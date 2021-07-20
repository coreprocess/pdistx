import argparse
from pathlib import Path

from .process import perform


def main():
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
        action='store_true',
        help='provide target as zip file',
    )

    parser.add_argument(
        'source',
        help='source path',
    )

    parser.add_argument(
        'target',
        help='target path (will be cleared)',
    )

    args = parser.parse_args()

    arg_define = {}

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
            arg_define[name] = value

    perform(
        Path(args.source).resolve(),
        Path(args.target).resolve(),
        arg_define,
        args.filter,
        args.zip,
    )


if __name__ == '__main__':
    main()
