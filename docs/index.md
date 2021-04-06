Convert Python packages into a single file that makes the distribution of your projects simpler and provides options for compressing the source code and zipping the output.

---

**Documentation**: <a href="https://3dninjas.github.io/pyscriptpacker/" target="_blank">https://3dninjas.github.io/pyscriptpacker/</a>

**Source Code**: <a href="https://github.com/3dninjas/pyscriptpacker" target="_blank">https://github.com/3dninjas/pyscriptpacker</a>

---

## Installation

```console
pip install pyscriptpacker
```

## Usage

```console
Usage: 
    python -m pyscriptpacker [options] module1,module2,.. path1,path2,.. output

Convert Python packages into a single file that makes the distribution of
your projects simpler and provides options for compressing the source code and
zipping the output.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -c, --compress        compress the sources
  -m main_file, --main=main_file
                        append main script to the bundle
  -z zip_file, --zip=zip_file
                        zip the bundle script
  -r path,..., --resources=path,...
                        add resource files and folders to the zip file, using
                        their basename or a custom path annotated with a
                        colon, e.g. -z ./res/logo.png:logo.png
```
