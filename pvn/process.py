from os import listdir, makedirs, walk
from pathlib import Path
from shutil import copy, rmtree
from subprocess import check_call
from tempfile import mkdtemp
from typing import List
from fnmatch import fnmatch

from .transform import import_transform

IGNORE = [
    '*.dist-info',
    '.git',
    '__pycache__',
    '*.pyc',
]


def _should_ignore(name: str):
    for entry in IGNORE:
        if fnmatch(name, entry):
            return True
    return False


def perform(
    requirements_files: List[Path],
    source_folders: List[Path],
    target_folder: Path,
    pip_cmd: str,
):
    tmp_source_folders = []

    try:
        # detect requirements.txt in target folder
        target_requirements_file = target_folder.joinpath('requirements.txt')
        if target_requirements_file.is_file():
            requirements_files.append(target_requirements_file)

        # create a source folder for each requirements
        for requirements_file in requirements_files:
            # create temp folder
            tmp_source_folder = Path(mkdtemp())
            tmp_source_folders.append(tmp_source_folder)
            source_folders.append(tmp_source_folder)

            # install packages into temp folder
            print(f'Installing {requirements_file} to {tmp_source_folder}...')
            check_call([
                pip_cmd, 'install', '--upgrade', '--requirement', requirements_file, '--target',
                str(tmp_source_folder)
            ])

        # clean target folder
        for entry_name in listdir(target_folder):
            if entry_name not in ['requirements.txt', '.gitignore']:
                entry_path = target_folder.joinpath(entry_name)
                if entry_path.is_dir() and not entry_path.is_symlink():
                    rmtree(entry_path)
                else:
                    entry_path.unlink()

        # build dictionary of modules
        modules: dict[str, Path] = {}

        for source_folder in source_folders:
            for entry_name in listdir(source_folder):
                # detect module name
                module_name = None
                entry_source_path = source_folder.joinpath(entry_name)

                if entry_source_path.is_dir():
                    if _should_ignore(entry_name) or entry_name in ['bin']:
                        continue
                    module_name = entry_name

                elif entry_source_path.is_file():
                    if not entry_name.endswith('.py'):
                        continue
                    module_name = entry_name[:-3]

                else:
                    continue

                # add to module dictionary
                if module_name in modules:
                    print(f'Warning: multiple copies of {module_name} detected, skipping redundant one!')
                    continue

                # add to dictionary
                modules[module_name] = entry_source_path

        module_names = list(modules.keys())

        # copy and transform all module files
        for module_name, module_source_path in modules.items():
            print(f'Processing {module_name} from {module_source_path}...')
            module_target_path = target_folder.joinpath(module_name)

            # handle file case
            if module_source_path.is_file():
                import_transform(module_source_path, module_target_path, 1, module_names)

            # handle directory case
            else:
                for sub_source_folder, folders, files in walk(module_source_path, followlinks=True):
                    # filter entries to be ignored (folders need to be modified in-place to take effect for os.walk)
                    folders[:] = [folder for folder in folders if not _should_ignore(folder)]
                    files = [file for file in files if not _should_ignore(file)]

                    # ensure sub target directory exists
                    sub_source_folder = Path(sub_source_folder)
                    sub_folder = sub_source_folder.relative_to(module_source_path)
                    sub_target_folder = target_folder.joinpath(module_name, sub_folder)
                    makedirs(sub_target_folder, exist_ok=True)

                    # transform or copy files
                    level = len(sub_folder.parts) + 1

                    for file in files:
                        source_file = sub_source_folder.joinpath(file)
                        target_file = sub_target_folder.joinpath(file)

                        if file.endswith('.py'):
                            import_transform(source_file, target_file, level, module_names)
                        else:
                            copy(source_file, target_file, follow_symlinks=True)

        # create empty init file in target folder
        open(target_folder.joinpath('__init__.py'), 'w').close()

    finally:
        # clean up temporary folders
        for tmp_source_folder in tmp_source_folders:
            print(f'Purging {tmp_source_folder}...')
            rmtree(tmp_source_folder, True)
