#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$(realpath "$( dirname "${BASH_SOURCE[0]}" )")"

# install packer
python3 -m venv ./env
source ./env/bin/activate
pip install --upgrade ../

# pack libraries
mkdir -p ./packed/libs
python -m pyscriptpacker tests,lib1,lib2,lib3 ./unpacked ./packed/libs/__init__.py
