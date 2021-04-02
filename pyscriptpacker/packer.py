import logging

from pyscriptpacker import utils
from pyscriptpacker import files
from pyscriptpacker import compression
from pyscriptpacker.modules import ModuleManager


def pack(
    module_names,
    search_paths,
    output,
    compress_src,
    minify_src,
    main_file,
    zip_file,
    resource_list,
):
    # Init module graph to build the dependencies data.
    module_manager = ModuleManager(compress_src, minify_src)
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
        main_content = module_manager.process_file_content(main_file)
        script += '\n' + main_content
    if minify_src:
        script = compression.minify_source(script)
    if compress_src:
        script = compression.compress_source(script)

    # Write either the target python file or a zip file
    if not zip_file:
        files.write_output(output, script)
    else:
        compression.zip_output(zip_file, script, output, resource_list)

    logging.info('Finish with %s error%s!', logging.error.counter,
                 '' if logging.error.counter <= 1 else 's')
