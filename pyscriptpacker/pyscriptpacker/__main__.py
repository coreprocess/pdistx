import sys
from optparse import OptionParser

from pyscriptpacker import __version__
from pyscriptpacker import packer


def parse_input(options, args):
    '''
    Check if the input options and arguments are valid and runs `packer.pack`
    with the given command line options.

    Args:
        options (dict): A dictionary contain all the options define in main().
        args (list): A list of input arguments.
    '''

    is_minify = options.minifier
    py_version = options.python_version
    output_path = args[0]
    lib_paths = args[1:]

    if py_version < '2.7' or py_version > '3.9':
        sys.stdout.write(
            'Error: pyscriptpacker not support python version '
            'lower than 2.7. Please see --help for more information.')
        sys.exit(1)

    packer.pack(py_version, is_minify, output_path, lib_paths)


def main():
    '''
    Sets up our command line options, prints the usage/help (if warranted).
    '''
    usage = ('%prog [options] <output-path> <library-path> [...]')
    if '__main__.py' in sys.argv[0]:  # python -m pyscriptpacker
        usage = ('pyscriptpacker [options] <output-path> <library-path> [...]')
    parser = OptionParser(usage=usage, version=__version__)
    parser.disable_interspersed_args()
    parser.add_option(
        '-p',
        '--python',
        dest='python_version',
        default='3.8',
        help=('Specify the python verson for packaging. '
              'Currently support: 2.7, 3.5, 3.6, 3.7, 3.8'),
        metavar='<python version>',
    )
    parser.add_option(
        '-m',
        '--minifier',
        action='store_true',
        dest='minifier',
        default=False,
        help='Minifier the Python file content using pyminifier.',
    )

    options, args = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(2)
    if len(args) < 2:  # TODO(Nghia Lam): Find more dynamic approach
        sys.stdout.write('Error: You must input all the required arguments. '
                         'Please see --help for more information.')
        sys.exit(2)

    parse_input(options, args)


if __name__ == '__main__':
    main()
