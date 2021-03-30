import os
import sys
import logging
import zipfile

from pyscriptpacker import utils
from pyscriptpacker.modules import ModuleManager


def _retrieve_file_paths(directory):
    '''
    Return all file paths of the particular directory.

    Args:
        directory (string): The directory to query all the file paths.
    '''
    file_paths = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_paths.append(file_path)
    return file_paths


def zip_output(output, zipped_list):
    output_dir = os.path.dirname(output)
    output_name = os.path.basename(output)

    zip_name = output_name.split('.')[0] + '.zip'
    zip_file = zipfile.ZipFile(os.path.join(output_dir, zip_name), 'w')
    zip_file.write(output, output_name)
    if 'None' not in zipped_list:
        for zipped in zipped_list:
            use_custom = ''
            zipped_target = zipped
            if ':' in zipped:
                zipped_target, use_custom = zipped.split(':')

            if not os.path.exists(zipped_target):
                logging.error('Cannot find this file/folder for zipping: %s',
                              zipped_target)
                continue
            if os.path.isdir(zipped_target):
                for file in _retrieve_file_paths(zipped_target):
                    filename = os.path.relpath(file, zipped_target)
                    if not use_custom:
                        base_dir = os.path.basename(os.path.normpath(zipped))
                        zip_file.write(file, os.path.join(base_dir, filename))
                    else:
                        zip_file.write(file, os.path.join(use_custom, filename))
            else:
                if not use_custom:
                    zip_file.write(zipped_target,
                                   os.path.basename(zipped_target))
                else:
                    zip_file.write(zipped_target, use_custom)

    zip_file.close()


def write_output(output_path, texts):
    try:
        with open(output_path, 'w') as output:
            output.write(texts)
    except IOError as e:
        sys.stdout.write('Error: Cannot write to ' + output_path +
                         '\nPlease make sure the directory is valid!!\n' +
                         str(e))
        sys.exit(1)


def pack(module_names, search_paths, output, main_file, compressed, zipped):
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

    if main_file:
        print(main_file)

    write_output(output, main_script)

    if zipped:
        zip_output(output, zipped)

    logging.info('Finish with %s error%s!', logging.error.counter,
                 '' if logging.error.counter <= 1 else 's')
