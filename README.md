## PyScriptPacker 2.0

Convert Python packages into a single file which makes the distribution of your projects easier. It can also provide a security layer to your code by parsing all the sources and compress them.

## Installation

```sh
pip install pyscriptpacker
```

## Usage

When you install PyScriptPacker, the `pyscriptpacker` will be added to your `$PATH`.

```
Usage: pyscriptpacker [options] -n <project>[,extra_projects,...] -o <output> <directory> [extra_dirs...]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit

  Primary Flags:
    -n <project names>, --names=<project names>
                        specify the projects will be packed.
    -o <output>, --output=<output>
                        specify the output packed file name (and location)

  Optional Flags:
    -z, --zip           zip the output into a zip file.
    -c, --compress      compress the Python source.
```
