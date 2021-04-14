<p align="center">
    <em>A better way for distributing your Python packages.</em>
</p>
<p align="center">
    <a href="https://github.com/3dninjas/pyscriptpacker/actions/workflows/unittests.yaml" target="_blank">
        <img src="https://github.com/3dninjas/pyscriptpacker/actions/workflows/unittests.yaml/badge.svg" alt="Test">
    </a>
    <a href="https://pypi.org/project/pyscriptpacker/" target="_blank">
        <img src="https://img.shields.io/pypi/v/pyscriptpacker?color=%2334D058&label=pypi%20package" alt="Package version">
    </a>
</p>

---

**Documentation**: <a href="https://3dninjas.github.io/pyscriptpacker/" target="_blank">https://3dninjas.github.io/pyscriptpacker/</a>

**Source Code**: <a href="https://github.com/3dninjas/pyscriptpacker" target="_blank">https://github.com/3dninjas/pyscriptpacker</a>

---

Pyscriptpacker helps converting your Python packages into a single file that makes the distribution of your projects much more simple.
The key features are:

- **Single file distribution:** The final result will be a single file module which allows the file can be easily placed into any other projects.
- **Extending libraries:** Pyscriptpacker support packing external modules to your project as long as it is a Python library and can be installed via pypi (or you can provide the path to the library manually).
- **Zip output:** The user can use Pyscriptpacker for zipping the output and other files/folder together with custom path support for a desired structure.
- **Compressing & minifying:** Pyscriptpacker has an option which can be used to compress and minify all the sources to add a security layer for your code.
- **Python 2 & 3:** Pyscriptpacker is compatible with both python 2 & 3, so it can support with projects with both versions.

Please see [feature](/features) for more information.

## Quick start

``` console
$ pip install pyscriptpacker

$ pyscriptpacker --help

Usage:
    python -m pyscriptpacker [options] module1,module2,.. path1,path2,.. output
```

Pyscriptpacker also provides a number of command line arguments.

`--version` 
:   > Show the Pyscriptpacker's version and exit.

`-h, --help`
:   > Show the Pyscriptpacker's help message and exit.

`-c mode, --compress mode`
:   > Default: `none` - This option allow to compress the sources and the packed file with 3 choices
    >
    >   - `none` : Do not compress anything. This is the default value.
    >   - `all` : Compress all the sources, included the packed file.
    >   - `modules` : Only compress the desired modules.

`-i, --minify`
:   !!! warning
        This option is heavily depended on the [pyminifier](https://github.com/liftoff/pyminifier) package, which is quite unstable, please use at your own risk.

    > Default: `false` - Minify the source code using the [pyminifier](https://github.com/liftoff/pyminifier) package, just like the **compress** option, it offers 3 choices:
    >
    >   - `none` : Do not minify anything. This is the default value.
    >   - `all` : Minify all the sources, included the packed file.
    >   - `modules` : Only minify the desired modules.
    

`-m main_file, --main=main_file`
:   > Default: `[]` - Append main file's script to the bundle, which allow it to be executed whenever we import the result file.

`-z zip_file, --zip=zip_file`
:   > Default: `None` - Zip the result script into the input zip file.

`-r path,..., --resources=path,...`
:   > Default: `[]` - Add resource files and folders to the zip file, using their basename or a custom path annotated with a colon, e.g. -z ./res/logo.png:logo.png

`-k package,..., --packages=package,...`
:   > Default: `[]` - install additional packages to a temporary virtual python environment, can be used for searching and packing.

`-p python_path, --python=python_path`
:   > Default: `sys.executable` - specify the python path used for the parameter of virtualenv tool. If this argument is not provided, pyscriptpacker will try getting the default path.

## License

**GNU General Public License v3.0**

Copyright (C) 2021 3D Ninjas GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
