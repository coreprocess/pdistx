import sys
import logging
from optparse import OptionParser, Option

from pyscriptpacker import __version__
from pyscriptpacker import packer
from pyscriptpacker.utils import CallCounted


class _CLIExtendOption(Option):
    '''
    Implementation of an option class for CLI OptionParser which has an
    action 'extend': take multiple values in a single comma-delimited string,
    and extend an existing list with them.
    Example:
        --names=foo,bar --names blah --names ding,dong
        -> ["foo", "bar", "blah", "ding", "dong"]
    Reference:
        https://docs.python.org/2/library/optparse.html#adding-new-actions
    '''
    ACTIONS = Option.ACTIONS + ('extend',)
    STORE_ACTIONS = Option.STORE_ACTIONS + ('extend',)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ('extend',)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ('extend',)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == 'extend':
            lvalue = value.split(',')
            values.ensure_value(dest, []).extend(lvalue)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)


def _assertion(condition, error_message):
    if not condition:
        logging.error('%s Please see --help for more information.',
                      error_message)
        sys.exit(1)


def _parse_input(
    module_names,
    search_paths,
    output,
    compressed,
    zipped_relative,
    zipped_absolute,
):
    '''
    Check if the input options and arguments are valid and run `packer.pack`
    with the given command line options.

    Args:
        module_names (list): List of module names the users want to pack.
        search_paths (list): List of path to search for modules.
        output (string): The output of the packed file.
        compressed (bool): Option for compressing the sources.
        zipped_list (list): List of files/folders which needed to be zipped
            with the output.
    '''
    _assertion(
        output,
        'pyscriptpacker needs the user specify the desired output file.')
    _assertion(
        len(module_names) >= 1,
        'pyscriptpacker needs at least one module name.')
    _assertion(
        len(search_paths) >= 1,
        'pyscriptpacker needs search paths contains the projects.')

    packer.pack(
        module_names,
        search_paths,
        output,
        compressed,
        zipped_relative,
        zipped_absolute,
    )


def main():
    '''
    Sets up our command line options, prints the usage/help (if warranted).
    '''
    # Logging initialization
    logging.basicConfig(level=logging.INFO,
                        format='[PyscriptPacker] %(levelname)s: %(message)s')
    logging.error = CallCounted(logging.error)

    # CLI
    usage = ('python -m pyscriptpacker [options] ' +
             'module1,module2,... path1,path2,... output')

    parser = OptionParser(option_class=_CLIExtendOption,
                          usage=usage,
                          version=__version__)
    parser.disable_interspersed_args()

    parser.add_option(
        '-c',
        '--compress',
        action='store_true',
        dest='compressed',
        default=False,
        help='compress the Python source.',
    )
    parser.add_option(
        '--zr',
        action='extend',
        dest='zipped_relative',
        default=[],
        help=('zip the output and the specified files/folders to the root of' +
              ' the zip file. User can provide None if only the output is ' +
              ' needed to be zipped.'),
        metavar='FILEs,FOLDERs,..',
    )
    parser.add_option(
        '--za',
        action='extend',
        dest='zipped_absolute',
        default=[],
        help=('zip the output and the specified files/folders to the zip' +
              ' file but maintain all the structures. User can provide None' +
              ' if only the output is needed to be zipped.'),
        metavar='FILEs,FOLDERs,..',
    )

    options, args = parser.parse_args()
    _assertion(len(args) == 3, 'Invalid usage of pyscriptpacker.')

    _parse_input(
        args[0].split(','),
        args[1].split(','),
        args[2],
        options.compressed,
        options.zipped_relative,
        options.zipped_absolute,
    )


if __name__ == '__main__':
    main()
