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


def get_setup_module_code(python_version):
    return (utils.py2_setup_code
            if python_version == '2.7' else utils.py3_setup_code)


def pack(project_names, output, directories, python_version, is_minify):
    main_script = 'import sys\n\n'

    # Init module graph to build the dependencies data.
    module_graph = graph.ModuleGraph(project_names, is_minify)
    module_graph.parse_paths(directories)

    main_script += '_modules = ' + str(module_graph.generate_data())
    main_script += '\n'

    main_script += get_setup_module_code(python_version)

    write_output(output, main_script)
