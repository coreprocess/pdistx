from glob import glob
from os import close, makedirs, walk
from pathlib import Path
from posixpath import splitext
from shutil import copy, rmtree
from tempfile import mkdtemp, mkstemp
from typing import List

from pdist.utils.path import fnmatch_any
from pdist.utils.zip import zipit

from .transform import variant_transform


def perform(
    source: Path,
    target: Path,
    definitions: dict,
    filters: List[Path],
    do_zip: bool,
):
    # list of temporary files and folders
    tmp_paths: List[Path] = []

    # temporary paths get cleaned automatically at the end of this block
    try:

        # purging target
        print(f'Purging {target}...')
        if target.exists():
            if target.is_dir():
                rmtree(target)
            else:
                target.unlink()

        # create target path
        if do_zip:
            # create temporary directory or file
            if source.is_dir():
                tmp_target = Path(mkdtemp())
            else:
                tmp_fh, tmp_target = mkstemp()
                close(tmp_fh)  # dump handle right away
                tmp_target = Path(tmp_target)

            # add to tmp paths for cleanup
            tmp_paths.append(tmp_target)
        else:
            tmp_target = target

        # handle source folder
        print(f'Processing {source}...')

        if source.is_dir():

            # find all files and folders we want to filter out
            filter_paths = []
            for filter_item in filters:
                filter_paths += [Path(filter_path) for filter_path in glob(str(filter_item), recursive=True)]

            # ensure target directory exists
            makedirs(tmp_target, exist_ok=True)

            # process all files
            for source_folder, folders, files in walk(source, followlinks=True):

                # ensure sub target directory exists
                source_folder = Path(source_folder)
                target_folder = tmp_target.joinpath(source_folder.relative_to(source))
                makedirs(target_folder, exist_ok=True)

                # filter entries to be ignored (folders need to be modified in-place to take effect for os.walk)
                def _folder_filter(folder: Path):
                    return not fnmatch_any(folder.name, ['__pycache__', '.git']) and folder not in filter_paths

                def _file_filter(file: Path):
                    return not fnmatch_any(file.name, ['*.pyc']) and file not in filter_paths

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
            makedirs(tmp_target.parent, exist_ok=True)

            # transform file
            variant_transform(source, tmp_target, definitions)

        # zip temporary target path to actual target path
        if do_zip:
            zipit(
                tmp_target,
                target,
                target.stem + splitext(source) if not source.is_dir() else '',
            )

    finally:
        # clean up temporary folders
        for tmp_path in tmp_paths:
            print(f'Purging {tmp_path}...')
            if tmp_path.is_dir():
                rmtree(tmp_path, True)
            else:
                tmp_path.unlink()
