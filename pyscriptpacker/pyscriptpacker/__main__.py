import sys
from optparse import OptionParser, OptionGroup, Option

from pyscriptpacker import __version__
from pyscriptpacker import packer

PYTHON_VERSIONS = ['2', '3', 'both']


class CLIExtendOption(Option):
    '''
    Implementation of an action of CLI which can take multiple values in a
    single comma-delimited string, and extend an existing list with them.

    Example:
        --names=foo,bar --names blah --names ding,dong
        -> ["foo", "bar", "blah", "ding", "dong"]

    Reference:
        https://docs.python.org/2/library/optparse.html#adding-new-actions
    '''
    ACTIONS = Option.ACTIONS + ('extend',)
    STORE_ACTIONS = Option.STORE_ACTIONS + ('extend',)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == 'extend':
            lvalue = value.split(',')
            values.ensure_value(dest, []).extend(lvalue)
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)


def main():
    '''
    Sets up our command line options, prints the usage/help (if warranted).
    '''
    usage = ('%prog [options] -n project,extra_projects,... ' +
             '-o <output> <directory> [extra_dirs...]')
    if '__main__.py' in sys.argv[0]:  # python -m pyscriptpacker
        usage = ('pyscriptpacker [options] -n project,extra_projects,... ' +
                 '-o <output> <directory> [extra_dirs...]')

    parser = OptionParser(usage=usage, version=__version__)
    parser.disable_interspersed_args()

    primary_opts = OptionGroup(
        parser,
        'Primary Flags',
    )
    primary_opts.add_option(
        '-n',
        '--names',
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
        '-p',
        '--python',
        dest='python_version',
        default='both',
        type='choice',
        choices=PYTHON_VERSIONS,
        help=('python version for output file, ' +
              'choose from "2", "3" or "both".'),
        metavar='<python version>',
    )
    sub_opts.add_option(
        '-m',
        '--minifier',
        action='store_true',
        dest='minifier',
        default=False,
        help='minify and compress the Python source.',
    )
    parser.add_option_group(sub_opts)

    options, args = parser.parse_args()

    parse_input(
        options.project_names,
        options.output,
        args[0:],
        options.python_version,
        options.minifier,
    )


def parse_input(
    project_names,
    output_path,
    directories,
    python_version,
    is_minify,
):
    '''
    Check if the input options and arguments are valid and run `packer.pack`
    with the given command line options.

    Args:
        options (dict): A dictionary contain all the options define in main().
        args (list): A list of input arguments.
    '''
    assertion(
        output_path,
        'Error: pyscriptpacker needs the user specify the desired output file.')
    assertion(
        len(project_names) >= 1,
        'Error: pyscriptpacker needs at least one project name.')
    assertion(
        len(directories) >= 1,
        'Error: pyscriptpacker needs directories contains the projects.')
    assertion(
        python_version in PYTHON_VERSIONS,
        'Error: pyscriptpacker does not support the input python version.')

    packer.pack(python_version, is_minify, output_path, directories)


def assertion(condition, error_message):
    if not condition:
        sys.stdout.write(error_message +
                         '\nPlease see --help for more information.')
        sys.exit(1)


if __name__ == '__main__':
    main()
