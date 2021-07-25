# Python Distribution Tools

## Installation

**Note:** the Python Distribution Tools require Python 3.9 or newer to run. But of course, the tools can translate code for older Python versions.

### Recommended: Use `pipx`

```sh
# find your Python 3.9 binary and use that one for the following commands
python --version
python3 --version
python3.9 --version

# install pipx to be able to run pypi packages directly
python -m pip install pipx

# run pdistx
pipx run pdistx vendor --help
pipx run pdistx variant --help
pipx run pdistx pack --help

# in case pipx is not in the path, you can run it as module
python -m pipx run pdistx vendor --help
python -m pipx run pdistx variant --help
python -m pipx run pdistx pack --help
```

### Alternative: Install `pdistx` and use it directly

```sh
# find your Python 3.9 binary and use that one for the following commands
python --version
python3 --version
python3.9 --version

# install pdistx
python -m pip install pdistx

# run pdistx
pvendor --help
pvariant --help
ppack --help

# in case pdistx is not in the path, you can run it as module
python -m pvendor --help
python -m pvariant --help
python -m ppack --help
```

## Python Vendoring Tool

Vendor libraries in a subpackage, which can be placed anywhere in a project.

```
$ pvendor --help
$ pdistx vendor --help

usage: pvendor [-h] [-r requirements] [-s source] [-p pip] [-k keep] [-z zip] target

positional arguments:
  target           target folder (will be cleared, except for the ones to be kept)

optional arguments:
  -h, --help       show this help message and exit
  -r requirements  install packages from requirements.txt
  -s source        copy modules from source folder
  -p pip           pip command (defaults to pip)
  -k keep          files or folders to be kept in the target folder (defaults to requirements.txt and .gitignore)
  -z zip           zip file path (target becomes relative path within zip file)
```

## Python Variant Exporter

Export a specific variant from a codebase.

```
$ pvariant --help
$ pdistx variant --help

usage: pvariant [-h] [-d name[:type]=value] [-f filter] [-z zip] source target

positional arguments:
  source                source path
  target                target path (will be cleared)

optional arguments:
  -h, --help            show this help message and exit
  -d name[:type]=value  define variables to be replaced, e.g. -d __VARIANT__=PRO -d __LICENSE_CHECK__:bool=True
  -f filter             defines files and folders to be filtered out (glob pattern)
  -z zip                zip file path (target becomes relative path within zip file)
```

## Python Packer Tool

Pack a Python package into a single Python file.

```
$ ppack --help
$ pdistx pack --help

usage: ppack [-h] [-r] [-m] [-f filter] [-z zip] source target

positional arguments:
  source      source package path
  target      target python (will be cleared)

optional arguments:
  -h, --help  show this help message and exit
  -r          create a resources folder with all non-python files (it will be named <target>_resources and be cleared)
  -m          use __main__.py of the package as bootstrap code (default is to use the root __init__.py of the package)
  -f filter   defines files and folders to be filtered out (glob pattern)
  -z zip      zip file path (target becomes relative path within zip file)
```

## Examples

### Blender Addon

```sh
# vendor packages
pvendor examples/blender_addon/vendor

# generate PRO as zip
pvariant \
    -d __VARIANT__=PRO                 \
    -f '**/free.bip'                   \
    -z $HOME/Desktop/blender_addon.zip \
    examples/blender_addon             \
    blender_addon

# generate FREE as folder
pvariant \
    -d __VARIANT__=FREE    \
    -f '**/pro.bip'        \
    examples/blender_addon \
    $HOME/.config/blender/2.93/scripts/addons/blender_addon

# pack addon as single file
ppack \
    -r \
    -f 'vendor/requirements.txt' -f 'vendor/.gitignore' \
    examples/blender_addon \
    $HOME/.config/blender/2.93/scripts/addons/blender_addon.py
```

### QT App

```sh
# vendor packages
pvendor examples/qt_app/vendor

# pack app as single file
ppack \
    -r \
    -f 'vendor/requirements.txt' -f 'vendor/.gitignore' \
    -m \
    examples/qt_app \
    $HOME/Desktop/qt_app.py
```
