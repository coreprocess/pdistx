from os import walk
from os.path import isdir, join, relpath
from zipfile import ZIP_DEFLATED, ZipFile


def zipit(source: str, target: str, base: str):
    with ZipFile(target, 'w', ZIP_DEFLATED) as handle:
        # zip directory
        if isdir(source):
            for root, _, files in walk(source):
                for file in files:
                    path = join(root, file)
                    handle.write(path, join(base, relpath(path, source)))

        # zip individual file
        else:
            handle.write(source, base)
