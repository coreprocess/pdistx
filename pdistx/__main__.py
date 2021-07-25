import sys

# avoid having the cwd in the path
# see https://docs.python.org/3/tutorial/modules.html#the-module-search-path
if '' in sys.path:
    sys.path.remove('')

from typing import List

from ppack.__main__ import main as main_pack
from pvariant.__main__ import main as main_variant
from pvendor.__main__ import main as main_vendor


def main(argv: List[str] = sys.argv[1:]):

    tool = argv[0] if len(argv) > 0 else None
    argv = argv[1:]

    if tool == 'pack':
        main_pack(argv)
    elif tool == 'variant':
        main_variant(argv)
    elif tool == 'vendor':
        main_vendor(argv)
    else:
        print('Usage: pdistx pack|variant|vendor --help')
        sys.exit(1)


if __name__ == '__main__':
    main()
