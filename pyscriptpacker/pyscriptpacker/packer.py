import os


def find_libraries(library_paths):
    for lib_path in library_paths:
        if os.path.exists(lib_path):
            for root, directories, files in os.walk(lib_path):
                for file in files:
                    if '__init__.py' in file:
                        print(os.path.join(root, file))


def pack(python_version, output_path, product_name, module_name, library_paths):
    # TODO(Nghia Lam): Support generate unique product name -> Confirm with
    # Niklas.
    find_libraries(library_paths)
