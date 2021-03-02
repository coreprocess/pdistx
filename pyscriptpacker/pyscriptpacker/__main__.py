import sys
from optparse import OptionParser

from pyscriptpacker import __version__
from pyscriptpacker import packer


def parse_input(options, args):
    """Check if the input options and arguments are valid and runs
    `packer.pack` with the given command line options.

    Args:
        options (dict): A dictionary contain all the options define in main().
        args (list): A list of input arguments.
    """

    if len(args) != 4:  # TODO(Nghia Lam): Find more dynamic approach
        sys.stdout.write('Error: You must give all the required arguments. '
                         'Please see --help for more information.')
        sys.exit(1)

    packer.pack(python_version=options.python_version,
                output_path=args[0],
                product_name=args[1],
                module_name=args[2],
                library_path=args[3])


def main():
    """
    Sets up our command line options, prints the usage/help (if warranted).
    """
    usage = ('%prog [options] ' +
             '<output-path> <product-name> <module-name> <library-path>')
    if '__main__.py' in sys.argv[0]:  # python -m pyscriptpacker
        usage = ('pyscriptpacker [options] ' +
                 '<output-path> <product-name> <module-name> <library-path>')
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

    options, args = parser.parse_args()

    if not args:
        parser.print_help()
        sys.stdout.write('\nUnknown input arguments !!')
        sys.exit(2)
    parse_input(options, args)


if __name__ == '__main__':
    main()
