from os import walk
from os.path import join, relpath
from zipfile import ZIP_DEFLATED, ZipFile


def zip_dir(source, target):
    with ZipFile(target, 'w', ZIP_DEFLATED) as handle:
        for root, _, files in walk(source):
            for file in files:
                file_path = join(root, file)
                handle.write(file_path, relpath(file_path, source))
