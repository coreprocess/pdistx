import sys
import logging
from optparse import OptionParser, Option

from pyscriptpacker import __version__, __doc__
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
    compress_src,
    minify_src,
    main_file,
    zip_file,
    resource_list,
    package_list,
    python_path,
):
    '''
    Check if the input options and arguments are valid and run `packer.pack`
    with the given command line options.

    Args:
        module_names (list): List of module names the users want to pack.
        search_paths (list): List of path to search for modules.
        output (string): The specification output of the packed file.
        compress_src (bool): Option for compressing the sources.
        minify_src (bool): Option for minifying the sources.
        main_file (string): The file whose source code will be executed when
            importing packed file.
        zip_file (string): Target zip file.
        resource_list (list): List of files/folders which will be added to the
            zip.
        package_list (list): List of packages which will be installed to the
            virtual environment.
        python_path (string): The path to the python executable used for
            creating the virtual environment command.
    '''
    _assertion(output, 'output path required.')
    _assertion(len(module_names) > 0, 'one module name required.')
    _assertion(
        len(search_paths) > 0 or len(package_list) > 0,
        'one search path or one package required.')

    packer.pack(
        module_names,
        search_paths,
        output,
        compress_src,
        minify_src,
        main_file,
        zip_file,
        resource_list,
        package_list,
        python_path,
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
    usage = 'python -m pyscriptpacker [options] module1,module2,.. path1,path2,.. output'

    parser = OptionParser(option_class=_CLIExtendOption,
                          usage=usage,
                          description=__doc__,
                          version=__version__)
    parser.disable_interspersed_args()

    parser.add_option(
        '-i',
        '--minify',
        type='choice',
        action='store',
        dest='minify_src',
        choices=['none', 'all', 'modules'],
        default='none',
        metavar='mode',
        help=
        ('minify the sources (unstable, not recommended), specify by three modes: "none", "all", "modules"'
        ),
    )
    parser.add_option(
        '-c',
        '--compress',
        type='choice',
        action='store',
        dest='compress_src',
        choices=['none', 'all', 'modules'],
        default='none',
        metavar='mode',
        help=
        ('compress the sources codes, specify by three modes: "none", "all", "modules"'
        ),
    )
    parser.add_option(
        '-m',
        '--main',
        dest='main_file',
        default=None,
        help='append main script to the bundle',
        metavar='main_file',
    )
    parser.add_option(
        '-z',
        '--zip',
        dest='zip_file',
        default=None,
        help=('zip the bundle script'),
        metavar='zip_file',
    )
    parser.add_option(
        '-r',
        '--resources',
        action='extend',
        dest='resource_list',
        default=[],
        help=
        ('add resource files and folders to the zip file, using their basename or a custom path annotated with a colon, e.g. -z ./res/logo.png:logo.png'
        ),
        metavar='path,...',
    )
    parser.add_option(
        '-k',
        '--packages',
        action='extend',
        dest='package_list',
        default=[],
        help=
        ('install additional packages to a temporary virtual python environment, can be used for searching and packing.'
        ),
        metavar='package,...',
    )
    parser.add_option(
        '-p',
        '--python',
        dest='python_path',
        default=[],
        help=
        ('specify the python path used for the parameter of virtualenv tool. If this argument is not provided, pyscriptpacker will try getting the default path.'
        ),
        metavar='python_path',
    )

    options, args = parser.parse_args()
    _assertion(len(args) == 3, 'Invalid usage of pyscriptpacker.')

    _parse_input(
        args[0].split(','),
        args[1].split(',') if args[1] != '-' else [],
        args[2],
        options.compress_src,
        options.minify_src,
        options.main_file,
        options.zip_file,
        options.resource_list,
        options.package_list,
        options.python_path,
    )


if __name__ == '__main__':
    main()
