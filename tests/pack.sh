#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$(realpath "$( dirname "${BASH_SOURCE[0]}" )")"

# pack libraries
mkdir -p ./packed
PYTHONPATH=.. python -m pyscriptpacker tests,lib1,lib2,lib3 ./unpacked ./packed/libs.py
