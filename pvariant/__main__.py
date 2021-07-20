import argparse
from pathlib import Path
from pprint import pprint

from .process import IfExists, perform


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

    # TODO: update args

    arg_input = Path(args.input).resolve()
    arg_output = Path(args.output).resolve()
    arg_ifexists = args.ifexists if args.ifexists else IfExists.replace
    arg_ignore = args.ignore if len(args.ignore) > 0 else ['.*', '*.pyc']
    arg_transform = args.transform if len(args.transform) > 0 else ['*.py']
    arg_copy = args.copy if len(args.copy) > 0 else ['*']
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

    print('if exists : ' + arg_ifexists.name)
    print('ignore    : ' + ', '.join(arg_ignore))
    print('transform : ' + ', '.join(arg_transform))
    print('copy      : ' + ', '.join(arg_copy))
    print('define    : ', end='')
    pprint(arg_define)
    print('')

    perform(
        arg_input,
        arg_output,
        arg_ifexists,
        arg_ignore,
        arg_transform,
        arg_copy,
        arg_define,
    )
    print('done')


if __name__ == '__main__':
    main()
