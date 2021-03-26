## PyScriptPacker 2.0

Convert Python packages into a single file which makes the distribution of your projects easier. It can also provide a security layer to your code by parsing all the sources and compress them.

## Installation

```sh
pip install pyscriptpacker
```

## Usage

When you install PyScriptPacker, the `pyscriptpacker` will be added to your `$PATH`.

```
Usage: pyscriptpacker [options] module1,module2,... path1,path2,... output

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -c, --compress        compress the Python source.
  --zr=FILEs,FOLDERs,..
                        zip the output and the specified files/folders to the
                        root of the zip file. User can provide None if only
                        the output is  needed to be zipped.
  --za=FILEs,FOLDERs,..
                        zip the output and the specified files/folders to the
                        zip file but maintain all the structures. User can
                        provide None if only the output is needed to be
                        zipped.
```
