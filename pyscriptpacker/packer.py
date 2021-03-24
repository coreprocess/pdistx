import os
import sys
import zipfile

from pyscriptpacker import utils
from pyscriptpacker.modules import ModuleManager


def write_output(output_path, texts):
    try:
        with open(output_path, 'w') as output:
            output.write(texts)
    except IOError as e:
        sys.stdout.write('Error: Cannot write to ' + output_path +
                         '\nPlease make sure the directory is valid!!\n' +
                         str(e))
        sys.exit(1)


def zip_output(output_path):
    zip_name = output_path.split('.')[0] + '.zip'
    zip_obj = zipfile.ZipFile(zip_name, 'w')
    if os.path.isdir(output_path):
        for folder, _, file_names in os.walk(output_path):
            for file_name in file_names:
                file_path = os.path.join(folder, file_name)
                zip_obj.write(file_path, file_name)
    else:
        zip_obj.write(output_path, os.path.basename(output_path))
    zip_obj.close()


def pack(project_names, output, directories, compressed, zipped):
    # Init module graph to build the dependencies data.
    module_manager = ModuleManager(compressed)
    module_manager.parse_paths(directories, project_names)

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

    if zipped:
        zip_output(output)
