import bz2
import base64


def compress_source(source):
    compressed_source = bz2.compress(source.encode('utf-8'))
    out = 'import bz2, base64\n'
    out += 'exec(bz2.decompress(base64.b64decode("'
    out += base64.b64encode(compressed_source).decode('utf-8')
    out += '")))\n'

    return out
