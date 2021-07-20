from pathlib import Path
from typing import List

from pdist.utils.path import rmpath


def perform(
    source: Path,
    target: Path,
    filters: List[Path],
    add_resources: bool,
    do_zip: bool,
):
    # list of temporary files and folders
    tmp_paths: List[Path] = []

    # temporary paths get cleaned automatically at the end of this block
    try:

        # source is expected to be a directory
        if not source.is_dir():
            raise ValueError('source is expected to be a directory')

        # purging target
        print(f'Purging {target}...')
        rmpath(target)

    finally:
        # clean up temporary folders
        for tmp_path in tmp_paths:
            print(f'Purging {tmp_path}...')
            rmpath(tmp_path)
