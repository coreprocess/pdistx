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


def pack(project_names, output, directories, compress):
    main_script = ''

    # Init module graph to build the dependencies data.
    module_graph = graph.ModuleGraph(compress)
    module_graph.parse_paths(directories, project_names)

    # Add all modules from module graph data
    main_script += '_modules = ['
    for data in module_graph.generate_data():
        main_script += '{\n'
        main_script += '"name": ' + '__name__ + ".' + data.get('name') + '" ,'
        main_script += '"is_package": ' + str(data.get('is_package')) + ','
        main_script += '"code": ' + repr(data.get('code')) + ','
        main_script += '},\n'
    main_script += ']\n'

    # Get the setup code to execute the module data
    main_script += utils.get_setup_code()

    write_output(output, main_script)
