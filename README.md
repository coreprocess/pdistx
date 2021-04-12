Pyscriptpacker
---

_A better way for distributing your Python packages._

<p align="left">
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
- **Python 2 & 3:** Pyscriptpacker is compatible with both python 2 & 3, so it can support with projects with both versions.

## Quick start

``` console
$ pip install pyscriptpacker
$ python -m pyscriptpacker --help

Usage: python -m pyscriptpacker [options] module1,module2,.. path1,path2,.. output

 Convert Python packages into a single file that makes the distribution of
your projects simpler and provides options for compressing the source code and
zipping the output.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -c, --compress        compress the sources
  -i, --minify          minify the sources (unstable, not recommended)
  -m main_file, --main=main_file
                        append main script to the bundle
  -z zip_file, --zip=zip_file
                        zip the bundle script
  -r path,..., --resources=path,...
                        add resource files and folders to the zip file, using
                        their basename or a custom path annotated with a
                        colon, e.g. -z ./res/logo.png:logo.png
  -k package,..., --packages=package,...
                        install additional packages to a temporary virtual
                        python environment, can be used for searching and
                        packing.
  -p python_path, --python=python_path
                        specify the python path used for the parameter of
                        virtualenv tool. If this argument is not provided,
                        pyscriptpacker will try getting the default path.
```
