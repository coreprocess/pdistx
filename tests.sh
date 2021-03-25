#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$(realpath "$( dirname "${BASH_SOURCE[0]}" )")"

# pack
./tests/pack.sh

# pytest
pip3 install --upgrade pytest
pytest tests -p no:warnings
