import os
import bz2
import base64
import logging
import zipfile

from pyminifier import minification
from pyminifier import token_utils

from .files import get_file_paths


class _MinifyConfig(object):
    '''
    Default configuration for the wrapper of the pyminifier plugins, this
    configs is mapping 1:1 with the options of the pyminifier.
    '''

    def __init__(self):
        self.replacement_length = 1
        # Turn off all these settings due to unstable status of the pyminifier.
        self.tabs = False
        self.use_nonlatin = False
        self.obfuscate = False
        self.obf_classes = False
        self.obf_functions = False
        self.obf_variables = False
        self.obf_import_methods = False
        self.obf_builtins = False


def minify_source(source):
    tokens = token_utils.listified_tokenizer(source)
    source = minification.minify(tokens, _MinifyConfig())
    # Need to list the token again for untokenizing
    tokens = token_utils.listified_tokenizer(source)
    result = token_utils.untokenize(tokens)

    return result


def compress_source(source):
    compressed_source = bz2.compress(source.encode('utf-8'))
    out = 'import bz2, base64\n'
    out += 'exec(bz2.decompress(base64.b64decode("'
    out += base64.b64encode(compressed_source).decode('utf-8')
    out += '")))\n'

    return out


def zip_output(zip_path, bundle_src, bundle_path, resource_list):
    zip_file = zipfile.ZipFile(zip_path, 'w')
    zip_file.writestr(os.path.relpath(bundle_path), bundle_src)

    for resource in resource_list:
        if ':' in resource:
            resource_path, target_path = resource.split(':')
        else:
            resource_path = resource
            target_path = os.path.basename(resource)

        if not os.path.exists(resource_path):
            logging.error('Cannot find resource: %s', resource_path)
            continue

        if os.path.isdir(resource_path):
            for file_path in get_file_paths(resource_path):
                entry_path = os.path.join(
                    target_path, os.path.relpath(file_path, resource_path))
                zip_file.write(file_path, entry_path)
        else:
            zip_file.write(resource_path, target_path)

    zip_file.close()
