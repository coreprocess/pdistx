PyScriptPacker 2.0
---

Convert Python packages into a single file which make the distribution of your projects become easier. It can also provide a security layer to your code by parsing all the sources and compress them.

## Installation

We will eventually move this to pypi for better package management. For the time being, we can clone this repository and install it manually.

```shell
git clone https://github.com/3dninjas/pyscriptpacker2.git pyscriptpacker
cd pyscriptpacker
python -m pip install --upgrade pip
pip install -e pyscriptpacker
```

## Usage

When you install pyscriptpacker it should automatically add a 'pyscriptpacker' Command Line Interface to your `$PATH`. This CLI has a number of command line arguments:

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
    -c, --compress      compress the Python source.
```
