from os import listdir, makedirs, walk
from pathlib import Path
from shutil import copy
from subprocess import check_call
from tempfile import mkdtemp
from typing import List

from pdistx.utils.path import fnmatch_any, rmpath
from pdistx.utils.source import write_source
from pdistx.utils.zip import zipit

from .transform import import_transform


def perform(
    requirements: List[Path],
    pip: str,
    sources: List[Path],
    target: Path,
    keep: List[str],
    zip_: Path,
):
    # ensure pre-conditions
    for requirement in requirements:
        assert requirement.is_file(), 'requirements.txt is expected to be a file'

    for source in sources:
        assert source.is_dir(), 'source path is expected to be a directory'

    if zip_:
        assert not target.is_absolute(), 'target path is expected to be relative'

    # list of temporary files and folders
    tmps: List[Path] = []

    # temporary paths get cleaned automatically at the end of this block
    try:

        # detect requirements.txt in target folder
        if not zip_:
            requirement = target.joinpath('requirements.txt')
            if requirement.is_file():
                requirements.append(requirement)

        # create a source folder for each requirements
        for requirement in requirements:
            # create temp folder
            install_folder = Path(mkdtemp())
            tmps.append(install_folder)
            sources.append(install_folder)

            # install packages into temp folder
            print(f'Installing {requirement} to {install_folder}...')
            check_call([
                pip, 'install', '--upgrade', '--no-dependencies', '--requirement', requirement, '--target',
                str(install_folder)
            ])

        # clean target folder
        if zip_:
            print(f'Purging {zip_}...')
            rmpath(zip_)
        else:
            print(f'Purging {target}...')
            if target.is_dir():
                # if target is not a zip, remove all except the entries to be kept
                if not zip_:
                    for name in listdir(target):
                        if not fnmatch_any(name, keep):
                            path = target.joinpath(name)
                            rmpath(path)

                # if target is a zip, remove entire folder
                else:
                    rmpath(target)
            else:
                # remove an existing target file in any case
                rmpath(target)

        # build dictionary of modules
        # pylint: disable=unsubscriptable-object
        modules: dict[str, Path] = {}

        for source in sources:
            for entry in listdir(source):
                # detect module name
                name = None
                path = source.joinpath(entry)

                if path.is_dir():
                    if fnmatch_any(entry, ['*.dist-info', '*.egg-info', 'bin', '__pycache__', '.git']):
                        continue
                    name = entry

                else:
                    if not entry.endswith('.py'):
                        continue
                    name = entry[:-3]

                # add to module dictionary
                if name in modules:
                    print(f'Warning: multiple copies of {name} detected, skipping redundant one!')
                    continue

                # add to dictionary
                modules[name] = path

        # create target path
        if zip_:
            intermediate = Path(mkdtemp())
            tmps.append(intermediate)
        else:
            makedirs(target, exist_ok=True)
            intermediate = target

        # copy and transform all module files
        for name, source in modules.items():
            print(f'Processing {name} from {source}...')

            # handle directory case
            if source.is_dir():
                for source_folder, folders, files in walk(source, followlinks=True):
                    # filter entries to be ignored (folders need to be modified in-place to take effect for os.walk)
                    folders[:] = [folder for folder in folders if not fnmatch_any(folder, ['__pycache__', '.git'])]
                    files = [file for file in files if not fnmatch_any(file, ['*.pyc'])]

                    # ensure sub target directory exists
                    source_folder = Path(source_folder)
                    package_folder = source_folder.relative_to(source)
                    target_folder = intermediate.joinpath(name, package_folder)
                    makedirs(target_folder, exist_ok=True)

                    # transform or copy files
                    level = len(package_folder.parts) + 1

                    for file in files:
                        source_file = source_folder.joinpath(file)
                        target_file = target_folder.joinpath(file)

                        if file.endswith('.py'):
                            import_transform(source_file, target_file, level, list(modules.keys()))
                        else:
                            copy(source_file, target_file, follow_symlinks=True)

            # handle file case
            else:
                import_transform(source, intermediate.joinpath(name + '.py'), 1, list(modules.keys()))

        # create empty init file in target folder
        write_source(intermediate.joinpath('__init__.py'), '')

        # zip temporary target path to actual target path
        if zip_:
            zipit(intermediate, zip_, target)

    finally:
        # clean up temporary folders
        for path in tmps:
            print(f'Purging {path}...')
            rmpath(path)
