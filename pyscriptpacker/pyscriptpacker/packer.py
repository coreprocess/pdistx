import os


def find_all_module_paths(library_paths):
    all_module_paths = []

    for lib_path in library_paths:
        if not os.path.exists(lib_path):
            continue

        for root, _, files in os.walk(lib_path):
            is_module = False
            for file in files:
                # TODO(Nghia Lam): exclude `setup.py` because some structure
                # does put the `setup.py` outside of the module folder, not
                # inside it. Do we have a better way to solve this?
                if '.py' in file and file != 'setup.py':
                    is_module = True
                    break
            if is_module and root not in all_module_paths:
                all_module_paths.append(root)

    return all_module_paths


def pack_modules(product_name, library_paths):
    modules = []

    # Add product base modules
    module_paths = find_all_module_paths(library_paths)
    for path in module_paths:
        for root, _, files in os.walk(path):
            for file in files:
                # Open file for reading
                with open(os.path.join(root, file), 'r') as file_data:
                    file_text = file_data.read()

                # Add to modules
                folder_name = os.path.basename(os.path.normpath(root))
                file_name = file.split('.py')[0]
                module_item = {
                    'name': (
                        ('.'.join([product_name, folder_name]))
                        if file == '__init__.py' else
                        ('.'.join([product_name, folder_name, file_name]))),
                    'is_package': file == '__init__.py',
                    'code': file_text,
                }
                modules.append(module_item)

    return modules


def pack(python_version, output_path, product_name, library_paths):
    # TODO(Nghia Lam): Support generate unique product name -> Confirm with
    # Niklas
    modules = pack_modules(product_name, library_paths)

    for module in modules:
        print(module)
