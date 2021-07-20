from glob import glob
from pathlib import Path
from tempfile import mkdtemp
from typing import List

from pdist.utils.path import rmpath


def perform(
    source: Path,
    target: Path,
    filters: List[Path],
    do_resources: bool,
    zip_: Path,
):
    # ensure pre-conditions
    assert source.is_dir(), 'source is expected to be a directory'

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

        # determine base directory and relative target path
        if zip_:
            intermediate_target = Path(mkdtemp())
            tmps.append(intermediate_target)
        else:
            intermediate_target = target.parent
            target = Path(target.name)

        # find all files and folders we want to filter out
        filter_paths = []
        for item in filters:
            filter_paths += [Path(filter_path) for filter_path in glob(str(item), recursive=True)]

        # ...
        ...

    finally:
        # clean up temporary folders
        for path in tmps:
            print(f'Purging {path}...')
            rmpath(path)
