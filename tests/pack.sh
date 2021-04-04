#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# install pyscriptpacker with require packages
pushd ../
python -m pip install -e .
popd

# project root
cd "$( dirname "${BASH_SOURCE[0]}" )"

# pack libraries
mkdir -p ./packed
PYTHONPATH=.. python -m pyscriptpacker -i -c -m ./unpacked/tests/__main__.py tests,lib1,lib2,lib3,lib4 ./unpacked ./packed/libs.py
