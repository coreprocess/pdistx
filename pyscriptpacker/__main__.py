import sys
from optparse import OptionParser

from pyscriptpacker import __version__
from pyscriptpacker import packer


def _assertion(condition, error_message):
    if not condition:
        sys.stdout.write(error_message +
                         '\nPlease see --help for more information.')
        sys.exit(1)


def _parse_input(module_names, search_paths, output, compressed):
    '''
    Check if the input options and arguments are valid and run `packer.pack`
    with the given command line options.

    Args:
        module_names (list): [description]
        search_paths (list): [description]
        output (string): [description]
        compressed (bool): [description]
    '''
    _assertion(
        output,
        'Error: pyscriptpacker needs the user specify the desired output file.')
    _assertion(
        len(module_names) >= 1,
        'Error: pyscriptpacker needs at least one module name.')
    _assertion(
        len(search_paths) >= 1,
        'Error: pyscriptpacker needs search paths contains the projects.')

    packer.pack(
        module_names,
        search_paths,
        output,
        compressed,
    )


def main():
    '''
    Sets up our command line options, prints the usage/help (if warranted).
    '''
    usage = ('%prog [options] module1,module2,... path1,path2,... output')
    if '__main__.py' in sys.argv[0]:  # python -m pyscriptpacker
        usage = ('pyscriptpacker [options] module1,module2,... ' +
                 'path1,path2,... output')

    parser = OptionParser(usage=usage, version=__version__)
    parser.disable_interspersed_args()

    parser.add_option(
        '-c',
        '--compress',
        action='store_true',
        dest='compressed',
        default=False,
        help='compress the Python source.',
    )

    options, args = parser.parse_args()
    _parse_input(
        args[0].split(','),
        args[1].split(','),
        args[2],
        options.compressed,
    )


if __name__ == '__main__':
    main()
