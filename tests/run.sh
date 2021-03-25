#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$( dirname "${BASH_SOURCE[0]}" )"

# setup venv
pip install virtualenv
virtualenv ./env
source ./env/bin/activate
python -m pip install --upgrade pip
pip install --upgrade pytest pytest-forked

# pack and test
./pack.sh
python -m pytest -rA
