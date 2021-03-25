import sys
from optparse import OptionParser, OptionGroup, Option

from pyscriptpacker import __version__
from pyscriptpacker import packer


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
        sys.stdout.write(error_message +
                         '\nPlease see --help for more information.')
        sys.exit(1)


def _parse_input(project_names, output, directories, compressed):
    '''
    Check if the input options and arguments are valid and run `packer.pack`
    with the given command line options.

    Args:
        options (dict): A dictionary contain all the options define in main().
        args (list): A list of input arguments.
    '''
    _assertion(
        output,
        'Error: pyscriptpacker needs the user specify the desired output file.')
    _assertion(
        len(project_names) >= 1,
        'Error: pyscriptpacker needs at least one project name.')
    _assertion(
        len(directories) >= 1,
        'Error: pyscriptpacker needs directories contains the projects.')

    packer.pack(project_names, output, directories, compressed)


def main():
    '''
    Sets up our command line options, prints the usage/help (if warranted).
    '''
    usage = ('%prog [options] -n <project>[,extra_projects,...]' +
             '-o <output> <directory> [extra_dirs...]')
    if '__main__.py' in sys.argv[0]:  # python -m pyscriptpacker
        usage = ('pyscriptpacker [options] -n <project>[,extra_projects,...] ' +
                 '-o <output> <directory> [extra_dirs...]')

    parser = OptionParser(option_class=_CLIExtendOption,
                          usage=usage,
                          version=__version__)
    parser.disable_interspersed_args()

    primary_opts = OptionGroup(
        parser,
        'Primary Flags',
    )
    primary_opts.add_option(
        '-n',
        '--names',
        action='extend',
        dest='project_names',
        default=[],
        help=('specify the projects will be packed.'),
        metavar='<project names>',
    )
    primary_opts.add_option(
        '-o',
        '--output',
        dest='output',
        help=('specify the output packed file name (and location)'),
        metavar='<output>',
    )
    parser.add_option_group(primary_opts)

    sub_opts = OptionGroup(
        parser,
        'Optional Flags',
    )
    sub_opts.add_option(
        '-c',
        '--compress',
        action='store_true',
        dest='compressed',
        default=False,
        help='compress the Python source.',
    )
    parser.add_option_group(sub_opts)

    options, args = parser.parse_args()

    _parse_input(
        options.project_names,
        options.output,
        args[0:],
        options.compressed,
    )


if __name__ == '__main__':
    main()
