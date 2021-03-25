#!/bin/bash

# strict mode
set -euo pipefail
IFS=$'\n\t'

# project root
cd "$(realpath "$( dirname "${BASH_SOURCE[0]}" )")"

# pack
./pack.sh

# utils
indent () {
    sed 's/^/    /'
}

unpacked () {
    echo "unpacked $1 (python 2):"
    python test_unpacked.py $1 2>&1 | indent
    echo "unpacked $1 (python 3):"
    python3 test_unpacked.py $1 2>&1 | indent
}

packed () {
    echo "packed $1 (python 2):"
    python test_packed.py $1 2>&1 | indent
    echo "packed $1 (python 3):"
    python3 test_packed.py $1 2>&1 | indent
}


# unpacked tests
unpacked 1 | indent
unpacked 2 | indent
unpacked 3 | indent
unpacked 4 | indent
unpacked 5 | indent
unpacked 6 | indent
unpacked 7 | indent
unpacked 8 | indent
unpacked 9 | indent
unpacked 10 | indent
unpacked 11 | indent
unpacked 12 | indent

# packed tests
packed 1 | indent
packed 2 | indent
packed 3 | indent
packed 4 | indent
packed 5 | indent
packed 6 | indent
packed 7 | indent
packed 8 | indent
packed 9 | indent
packed 10 | indent
packed 11 | indent
packed 12 | indent
