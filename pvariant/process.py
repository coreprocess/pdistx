from glob import glob
from os import makedirs, walk
from pathlib import Path
from shutil import copy, rmtree
from typing import List

from pdist.utils.path import fnmatch_any

from .transform import variant_transform


def perform(
    source: Path,
    target: Path,
    definitions: dict,
    filters: List[Path],
    do_zip: bool,
):
    # purging target
    print(f'Purging {target}...')
    if target.exists():
        if target.is_dir():
            rmtree(target)
        else:
            target.unlink()

    # handle source folder
    print(f'Processing {source}...')

    if source.is_dir():

        # find all files and folders we want to filter out
        filter_paths = []
        for filter_item in filters:
            filter_paths += [Path(filter_path) for filter_path in glob(str(filter_item), recursive=True)]

        # process all files
        for source_folder, folders, files in walk(source, followlinks=True):

            # ensure sub target directory exists
            source_folder = Path(source_folder)
            target_folder = target.joinpath(source_folder.relative_to(source))
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
    elif source.is_file():

        # ensure sub target directory exists
        makedirs(target.parent, exist_ok=True)

        # transform file
        variant_transform(source, target, definitions)
