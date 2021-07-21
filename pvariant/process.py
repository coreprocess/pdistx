from os import close, makedirs, walk
from pathlib import Path
from shutil import copy
from tempfile import mkdtemp, mkstemp
from typing import List

from pdistx.utils.path import fnmatch_any, rmpath
from pdistx.utils.zip import zipit

from .transform import variant_transform


def perform(
    source: Path,
    target: Path,
    definitions: dict,
    filters: List[Path],
    zip_: Path,
):
    # ensure pre-conditions
    assert source.is_file() or source.is_dir(), 'source path is expected to be a file or directory'

    if zip_:
        assert not target.is_absolute(), 'target path is expected to be relative'

    # list of temporary files and folders
    tmps: List[Path] = []

    # temporary paths get cleaned automatically at the end of this block
    try:

        # purging target or zip
        if zip_:
            print(f'Purging {zip_}...')
            rmpath(zip_)
        else:
            print(f'Purging {target}...')
            rmpath(target)

        # create target path
        if zip_:
            # create interim directory or file
            if source.is_dir():
                intermediate = Path(mkdtemp())
            else:
                tmp_fh, intermediate = mkstemp()
                close(tmp_fh)  # dump handle right away
                intermediate = Path(intermediate)

            # add to tmp paths for cleanup
            tmps.append(intermediate)
        else:
            intermediate = target

        # handle source folder
        print(f'Processing {source}...')

        if source.is_dir():

            # ensure target directory exists
            makedirs(intermediate, exist_ok=True)

            # process all files
            for source_folder, folders, files in walk(source, followlinks=True):

                # ensure target directory exists
                source_folder = Path(source_folder)
                target_folder = intermediate.joinpath(source_folder.relative_to(source))
                makedirs(target_folder, exist_ok=True)

                # filter entries to be ignored (folders need to be modified in-place to take effect for os.walk)
                def _folder_filter(folder: Path):
                    return not fnmatch_any(folder.name, ['__pycache__', '.git']) and folder not in filters

                def _file_filter(file: Path):
                    return not fnmatch_any(file.name, ['*.pyc']) and file not in filters

                folders[:] = [folder for folder in folders if _folder_filter(source_folder.joinpath(folder))]
                files = [file for file in files if _file_filter(source_folder.joinpath(file))]

                # transform or copy file
                for file in files:
                    source_file = source_folder.joinpath(file)
                    target_file = target_folder.joinpath(file)

                    if file.endswith('.py'):
                        variant_transform(source_file, target_file, definitions)
                    else:
                        copy(source_file, target_file, follow_symlinks=True)

        # handle source file
        else:

            # ensure parent target directory exists
            makedirs(intermediate.parent, exist_ok=True)

            # transform file
            variant_transform(source, intermediate, definitions)

        # zip intermediate path to zip path
        if zip_:
            zipit(intermediate, zip_, target)

    finally:
        # clean up temporary folders
        for path in tmps:
            print(f'Purging {path}...')
            rmpath(path)
