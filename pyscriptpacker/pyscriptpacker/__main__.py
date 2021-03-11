import sys
from optparse import OptionParser

from pyscriptpacker import __version__
from pyscriptpacker import packer


def parse_input(python_version, is_minify, output_path, lib_paths):
    '''
    Check if the input options and arguments are valid and run `packer.pack`
    with the given command line options.

    Args:
        options (dict): A dictionary contain all the options define in main().
        args (list): A list of input arguments.
    '''
    if python_version < '2.7' or python_version > '3.9':
        sys.stdout.write(
            'Error: pyscriptpacker not support python version '
            'lower than 2.7. Please see --help for more information.')
        sys.exit(1)

    packer.pack(python_version, is_minify, output_path, lib_paths)


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
              'Currently support: 2.7, 3.5, 3.6, 3.7, 3.8, 3.9'),
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
    if len(args) < 2:
        sys.stdout.write('Error: You must input all the required arguments. '
                         'Please see --help for more information.')
        sys.exit(2)

    parse_input(options.python_version, options.minifier, args[0], args[1:])


if __name__ == '__main__':
    main()
