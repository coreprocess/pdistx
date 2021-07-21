from os import walk
from os.path import join, relpath
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def zipit(source_path: Path, zip_path: Path, base_path: Path):

    # check pre-conditions
    assert not base_path.is_absolute(), 'zip base path is expected to be relative'

    # create zip file
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as handle:

        # zip directory
        if source_path.is_dir():
            for root, _, files in walk(source_path):
                for file in files:
                    path = join(root, file)
                    handle.write(path, join(base_path, relpath(path, source_path)))

        # zip individual file
        else:
            handle.write(str(source_path), str(base_path))
