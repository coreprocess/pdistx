import sys
from optparse import OptionParser

from . import __version__


def main():
    """
    Sets up our command line options, prints the usage/help (if warranted), and
    runs :py:func:`` with the given command line options.
    """
    usage = ('%prog [options] ' +
             '<output-path> <product-name> <module-name> <library-path> [...]')
    if '__main__.py' in sys.argv[0]:  # python -m pyscriptpacker
        usage = (
            'pyscriptpacker [options] ' +
            '<output-path> <product-name> <module-name> <library-path> [...]')
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

    parser.print_help()


if __name__ == '__main__':
    main()
