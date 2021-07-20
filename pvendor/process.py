from os import listdir, makedirs, walk
from pathlib import Path
from shutil import copy, rmtree
from subprocess import check_call
from tempfile import mkdtemp
from typing import List

from pdist.utils.path import fnmatch_any
from pdist.utils.zip import zipit

from .transform import import_transform


def perform(
    requirements_files: List[Path],
    pip_cmd: str,
    source_folders: List[Path],
    target_path: Path,
    keep_names: List[str],
    do_zip: bool,
):
    # list of temporary files and folders
    tmp_paths: List[Path] = []

    # temporary paths get cleaned automatically at the end of this block
    try:

        # detect requirements.txt in target folder
        if not do_zip:
            target_requirements_file = target_path.joinpath('requirements.txt')
            if target_requirements_file.is_file():
                requirements_files.append(target_requirements_file)

        # create a source folder for each requirements
        for requirements_file in requirements_files:
            # create temp folder
            tmp_source_folder = Path(mkdtemp())
            tmp_paths.append(tmp_source_folder)
            source_folders.append(tmp_source_folder)

            # install packages into temp folder
            print(f'Installing {requirements_file} to {tmp_source_folder}...')
            check_call([
                pip_cmd, 'install', '--upgrade', '--requirement', requirements_file, '--target',
                str(tmp_source_folder)
            ])

        # clean target folder
        print(f'Purging {target_path}...')
        if target_path.is_dir():
            # if target is not a zip, remove all except the entries to be kept
            if not do_zip:
                for entry_name in listdir(target_path):
                    if not fnmatch_any(entry_name, keep_names):
                        entry_path = target_path.joinpath(entry_name)
                        if entry_path.is_dir() and not entry_path.is_symlink():
                            rmtree(entry_path)
                        else:
                            entry_path.unlink()

            # if target is a zip, remove entire folder
            else:
                rmtree(target_path)
        else:
            # unlink an existing target file in any case
            target_path.unlink()

        # build dictionary of modules
        # pylint: disable=unsubscriptable-object
        modules: dict[str, Path] = {}

        for source_folder in source_folders:
            for entry_name in listdir(source_folder):
                # detect module name
                module_name = None
                entry_source_path = source_folder.joinpath(entry_name)

                if entry_source_path.is_dir():
                    if fnmatch_any(entry_name, ['*.dist-info', 'bin', '__pycache__', '.git']):
                        continue
                    module_name = entry_name

                else:
                    if not entry_name.endswith('.py'):
                        continue
                    module_name = entry_name[:-3]

                # add to module dictionary
                if module_name in modules:
                    print(f'Warning: multiple copies of {module_name} detected, skipping redundant one!')
                    continue

                # add to dictionary
                modules[module_name] = entry_source_path

        module_names = list(modules.keys())

        # create target path
        if do_zip:
            tmp_target_path = Path(mkdtemp())
            tmp_paths.append(tmp_target_path)
        else:
            makedirs(target_path, exist_ok=True)
            tmp_target_path = target_path

        # copy and transform all module files
        for module_name, module_source_path in modules.items():
            print(f'Processing {module_name} from {module_source_path}...')

            # handle directory case
            if module_source_path.is_dir():
                for cur_source_folder, folders, files in walk(module_source_path, followlinks=True):
                    # filter entries to be ignored (folders need to be modified in-place to take effect for os.walk)
                    folders[:] = [folder for folder in folders if not fnmatch_any(folder, ['__pycache__', '.git'])]
                    files = [file for file in files if not fnmatch_any(file, ['*.pyc'])]

                    # ensure sub target directory exists
                    cur_source_folder = Path(cur_source_folder)
                    cur_folder = cur_source_folder.relative_to(module_source_path)
                    cur_target_path = tmp_target_path.joinpath(module_name, cur_folder)
                    makedirs(cur_target_path, exist_ok=True)

                    # transform or copy files
                    level = len(cur_folder.parts) + 1

                    for file in files:
                        source_file = cur_source_folder.joinpath(file)
                        target_file = cur_target_path.joinpath(file)

                        if file.endswith('.py'):
                            import_transform(source_file, target_file, level, module_names)
                        else:
                            copy(source_file, target_file, follow_symlinks=True)

            # handle file case
            else:
                import_transform(module_source_path, tmp_target_path.joinpath(module_name + '.py'), 1, module_names)

        # create empty init file in target folder
        with open(tmp_target_path.joinpath('__init__.py'), 'w'):
            pass

        # zip temporary target path to actual target path
        if do_zip:
            zipit(tmp_target_path, target_path, target_path.stem)

    finally:
        # clean up temporary folders
        for tmp_path in tmp_paths:
            print(f'Purging {tmp_path}...')
            if tmp_path.is_dir():
                rmtree(tmp_path, True)
            else:
                tmp_path.unlink()
