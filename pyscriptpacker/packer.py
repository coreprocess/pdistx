import os
import sys
import zipfile

from pyscriptpacker import utils
from pyscriptpacker.modules import ModuleManager


def zip_output(output, zipped_list):
    output_dir = os.path.dirname(output)
    output_name = os.path.basename(output)
    zip_name = output_name.split('.')[0] + '.zip'
    with zipfile.ZipFile(os.path.join(output_dir, zip_name), 'w') as zip_file:
        zip_file.write(output, output_name)
        if 'None' not in zipped_list:
            pass


def write_output(output_path, texts):
    try:
        with open(output_path, 'w') as output:
            output.write(texts)
    except IOError as e:
        sys.stdout.write('Error: Cannot write to ' + output_path +
                         '\nPlease make sure the directory is valid!!\n' +
                         str(e))
        sys.exit(1)


def pack(module_names, search_paths, output, compressed, zipped_list):
    # Init module graph to build the dependencies data.
    module_manager = ModuleManager(compressed)
    module_manager.parse_paths(search_paths, module_names)

    # Add all modules from module graph data
    main_script = '_virtual_modules = {\n'
    for data in module_manager.generate_data():
        main_script += '    "' + data.get('name') + '": {\n'
        main_script += '        "is_package": ' + str(
            data.get('is_package')) + ',\n'
        main_script += '        "code": ' + repr(data.get('code')) + ',\n'
        main_script += '    },\n'
    main_script += '}\n\n'

    # Get the setup code to execute the module data
    main_script += utils.get_setup_code()

    write_output(output, main_script)

    if zipped_list != []:
        zip_output(output, zipped_list)
