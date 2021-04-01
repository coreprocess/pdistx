import logging

from pyscriptpacker import utils
from pyscriptpacker import files
from pyscriptpacker import compression
from pyscriptpacker.modules import ModuleManager


def pack(module_names, search_paths, output, main_file, compressed, zipped):
    # Init module graph to build the dependencies data.
    module_manager = ModuleManager(compressed)
    module_manager.parse_paths(search_paths, module_names)

    # Add all modules from module graph data
    script = '_virtual_modules = {\n'
    for data in module_manager.generate_data():
        script += '    "' + data.get('name') + '": {\n'
        script += '        "is_package": ' + str(data.get('is_package')) + ',\n'
        script += '        "code": ' + repr(data.get('code')) + ',\n'
        script += '    },\n'
    script += '}\n\n'

    # Get the setup code to execute the module data
    script += utils.get_setup_code()

    if main_file:
        main_content = files.get_file_content(main_file)
        if compressed:
            main_content = compression.compress_source(main_content)
        script += '\n' + main_content

    files.write_output(output, script)

    if zipped:
        compression.zip_output(output, zipped)

    logging.info('Finish with %s error%s!', logging.error.counter,
                 '' if logging.error.counter <= 1 else 's')
