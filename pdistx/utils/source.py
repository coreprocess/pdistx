import ast
import re
from pathlib import Path


def detect_source_encoding(path: Path):
    # according to PEP 0263
    # https://www.python.org/dev/peps/pep-0263/

    # read first two lines
    with open(path, 'rb') as file:
        lines = [file.readline(), file.readline()]

    # check if first line starts with a bom
    if lines[0].startswith(b'\xef\xbb\xbf'):
        return 'utf-8'

    # check for encoding marker
    for line in lines:
        m = re.match(rb'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)', line)
        if m:
            return m.group(1).decode('latin-1')

    # default encoding
    return 'utf-8'


def read_source(path: Path):
    # detect encoding
    encoding = detect_source_encoding(path)

    # read code with proper encoding
    with open(path, 'r', encoding=encoding) as file:
        code = file.read()

    # remove all comments including encoding marker and shebang
    # NOTE: purposely done on read and write to cover all cases of pack/vendor/variant
    return ast.unparse(ast.parse(code))


def write_source(path: Path, code: str):

    # remove all comments including encoding marker and shebang
    # NOTE: purposely done on read and write to cover all cases of pack/vendor/variant
    code = ast.unparse(ast.parse(code))

    # prepend utf-8 encoding and final newline
    code = '# coding: utf-8\n' + code

    if not code.endswith('\n'):
        code += '\n'

    # write code as utf-8
    with open(path, 'w', encoding='utf-8') as file:
        file.write(code)
