import sys

from pyscriptpacker import utils
from pyscriptpacker import graph


def write_output(output_path, texts):
    try:
        with open(output_path, 'w') as output:
            output.write(texts)
    except IOError as e:
        sys.stdout.write('Error: Cannot write to ' + output_path +
                         '\nPlease make sure the directory is valid!!\n' +
                         str(e))
        sys.exit(1)


def pack(project_names, output, directories, is_minify):
    main_script = ''

    # Init module graph to build the dependencies data.
    module_graph = graph.ModuleGraph(is_minify)
    module_graph.parse_paths(directories, project_names)

    main_script += '_modules = ' + str(module_graph.generate_data())
    main_script += '\n'

    main_script += utils.get_setup_code()

    write_output(output, main_script)
