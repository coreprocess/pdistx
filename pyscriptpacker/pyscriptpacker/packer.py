import os
import sys

from pyscriptpacker import utils
from pyscriptpacker import graph


def write_output(output_path, texts):
    try:
        with open(output_path, 'w') as output:
            # TODO(Nghia Lam): Something wrong with new line characters '\n',
            # it cannot write a new line ...
            output.write(texts)
    except IOError as e:
        sys.stdout.write('Error: Cannot write to ' + output_path +
                         '\nPlease make sure the directory is valid!!\n' +
                         str(e))
        sys.exit(1)


def get_setup_module_code(python_version):
    return (utils.py2_setup_code
            if python_version == '2.7' else utils.py3_setup_code)


def pack(python_version, output_path, product_name, library_paths):
    main_script = 'import sys\n'

    module_graph = graph.ModuleGraph()
    module_graph.parse_paths(library_paths)
    print(module_graph.modules)
