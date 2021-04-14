#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$( dirname "${BASH_SOURCE[0]}" )"

# setup venv
python -m pip install --upgrade --user virtualenv
python -m virtualenv ./env
source ./env/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade pytest pytest-forked
python -m pip install -e ..

# pack libraries
mkdir -p ./packed
python -m pyscriptpacker -c all -m ./unpacked/tests/__main__.py -k pypng tests,lib1,lib2,lib3,lib4,png ./unpacked ./packed/libs.py

# run tests
python -m pytest -rA
