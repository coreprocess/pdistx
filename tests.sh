#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$(realpath "$( dirname "${BASH_SOURCE[0]}" )")"
{
    python3 -m venv ./envs
} || {
    pip install virtualenv && virtualenv -p /usr/bin/python ./envs
}
source ./envs/bin/activate

# pack
./tests/pack.sh

# pytest
pip install --upgrade pytest
pytest tests -p no:warnings
