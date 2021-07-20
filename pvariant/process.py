from fnmatch import fnmatch
from glob import glob
from os import makedirs, walk
from pathlib import Path
from shutil import copy, rmtree
from typing import List

from .transform import variant_transform


def _fnmatch_any(name: str, patterns: List[str]):
    for pattern in patterns:
        if fnmatch(name, pattern):
            return True
    return False


def perform(
    source: Path,
    target: Path,
    definitions: dict,
    filters: List[str],
    zip: bool,
):
    # prune target
    if target.exists():
        if target.is_dir():
            rmtree(target)
        else:
            target.unlink()

    # handle source folder
    if source.is_dir():

        # find all files and folders we want to filter out
        filter_paths = []
        for filter_item in filters:
            filter_paths += [Path(filter_path).resolve() for filter_path in glob(filter_item, recursive=True)]

        # process all files
        for sub_source_folder, folders, files in walk(source, followlinks=True):
            # filter entries to be ignored (folders need to be modified in-place to take effect for os.walk)
            def _folder_filter(folder):
                return not _fnmatch_any(folder, ['__pycache__', '.git']) and Path(folder).resolve() not in filter_paths

            def _file_filter(file):
                return not _fnmatch_any(file, ['*.pyc']) and Path(file).resolve() not in filter_paths

            folders[:] = [folder for folder in folders if _folder_filter(folder)]
            files = [file for file in files if _file_filter(file)]

            # ensure sub target directory exists
            sub_source_folder = Path(sub_source_folder)
            sub_target_folder = target.joinpath(sub_source_folder.relative_to(source))
            makedirs(sub_target_folder, exist_ok=True)

            # transform or copy file
            for file in files:
                source_file = sub_source_folder.joinpath(file)
                target_file = sub_target_folder.joinpath(file)

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
