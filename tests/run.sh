#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$(realpath "$( dirname "${BASH_SOURCE[0]}" )")"

# setup venv
{
    python3 -m venv ./env
} || {
    pip install virtualenv && virtualenv -p /usr/bin/python ./env
}
source ./env/bin/activate
python -m pip install --upgrade pip
pip install --upgrade pytest pytest-forked

# pack and test
./pack.sh
python -m pytest -rA
