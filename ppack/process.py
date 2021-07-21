from collections import OrderedDict
from hashlib import md5
from os import makedirs, walk
from pathlib import Path
from shutil import copy
from tempfile import mkdtemp
from typing import Dict, List

from pdist.utils.path import fnmatch_any, rmpath
from pdist.utils.zip import zipit


def perform(
    source: Path,
    target: Path,
    filters: List[Path],
    resources: bool,
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
            intermediate = Path(mkdtemp())
            tmps.append(intermediate)
        else:
            intermediate = target.parent
            target = Path(target.name)

        # prepare output paths
        packed = intermediate.joinpath(target.parent, target)

        if resources:
            resources_root = intermediate.joinpath(target.parent, target.stem + '_resources')

        # process all files
        modules: Dict[str, (str, bool)] = {}

        for source_folder, folders, files in walk(source, followlinks=True):

            # prepare folders
            source_folder = Path(source_folder)
            package_folder = source_folder.relative_to(source)

            if resources:
                resource_folder = resources_root.joinpath(package_folder)

            # filter entries to be ignored (folders need to be modified in-place to take effect for os.walk)
            def _folder_filter(folder: Path):
                return not fnmatch_any(folder.name, ['__pycache__', '.git']) and folder not in filters

            def _file_filter(file: Path):
                return not fnmatch_any(file.name, ['*.pyc']) and file not in filters

            folders[:] = [folder for folder in folders if _folder_filter(source_folder.joinpath(folder))]
            files = [file for file in files if _file_filter(source_folder.joinpath(file))]

            # read or copy file
            for file in files:
                source_file = source_folder.joinpath(file)

                # read module codes
                if file.endswith('.py'):
                    # determine module name
                    is_package = file == '__init__.py'

                    name = list(package_folder.parts)
                    name += [file.split('.')[0]] if not is_package else []

                    name = '.'.join(name)

                    # load module code
                    with open(source_file) as source_handle:
                        modules[name] = (source_handle.read(), is_package)

                # copy resource files
                else:
                    if resources:
                        makedirs(resource_folder, exist_ok=True)
                        copy(source_file, resource_folder.joinpath(file), follow_symlinks=True)

        if len(modules) == 0:
            raise ValueError('no modules found')

        # create all missing intermediate packages
        for name in list(modules.keys()):
            parts = name.split('.')
            for i in range(1, len(parts)):
                package = '.'.join(parts[0:i])
                if package not in modules:
                    modules[package] = ('', True)

        # ensure stable ordering
        modules = OrderedDict(sorted(modules.items(), key=lambda i: i[0]))

        # determine bootstrap module
        mode = 'main'
        bootstrap, _ = modules.get('__main__', (None, None))

        if bootstrap is None:
            mode = 'package'
            bootstrap, _ = modules['']

        # generate hash
        modules = repr(modules)
        hash_ = md5(modules.encode('utf-8')).hexdigest()

        # create packed file
        with open(Path(__file__).parent.joinpath('template.py'), 'r') as file:
            code = file.readlines()

        for i in range(len(code)):
            if '    pack_mode = \'\'\n' == code[i]:
                code[i] = '    pack_mode = ' + repr(mode) + '\n'
            elif '    pack_name = \'\'\n' == code[i]:
                code[i] = '    pack_name = ' + repr(source.name) + '\n'
            elif '    pack_hash = \'\'\n' == code[i]:
                code[i] = '    pack_hash = ' + repr(hash_) + '\n'
            elif '    pack_modules = {}\n' == code[i]:
                code[i] = '    pack_modules = ' + modules + '\n'

        code = ''.join(code) + '\n\n' + bootstrap

        print(f'Writing {packed}...')
        with open(packed, 'w') as file:
            file.write(code)

        # zip intermediate path to zip path
        if zip_:
            print(f'Packing {zip_}...')
            zipit(intermediate, zip_, Path(''))

    finally:
        # clean up temporary folders
        for path in tmps:
            print(f'Purging {path}...')
            rmpath(path)
