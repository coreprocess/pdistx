import os
import bz2
import base64
import logging
import zipfile

from pyscriptpacker.files import get_file_paths


def compress_source(source):
    compressed_source = bz2.compress(source.encode('utf-8'))
    out = 'import bz2, base64\n'
    out += 'exec(bz2.decompress(base64.b64decode("'
    out += base64.b64encode(compressed_source).decode('utf-8')
    out += '")))\n'

    return out


def zip_output(output, zipped_list):
    output_dir = os.path.dirname(output)
    output_name = os.path.basename(output)

    zip_name = output_name.split('.')[0] + '.zip'
    zip_file = zipfile.ZipFile(os.path.join(output_dir, zip_name), 'w')
    zip_file.write(output, output_name)

    if 'None' not in zipped_list:
        for zipped in zipped_list:
            use_custom = ''
            zipped_target = zipped
            if ':' in zipped:
                zipped_target, use_custom = zipped.split(':')
            if not os.path.exists(zipped_target):
                logging.error('Cannot find this file/folder for zipping: %s',
                              zipped_target)
                continue
            # Add target to zip file
            if os.path.isdir(zipped_target):
                _add_folder_to_zipfile(zip_file, zipped_target, use_custom)
            else:
                _add_file_to_zipfile(zip_file, zipped_target, use_custom)

    zip_file.close()


def _add_folder_to_zipfile(zip_file, folder, custom_name=None):
    for file in get_file_paths(folder):
        filename = os.path.relpath(file, folder)
        if not custom_name:
            base_dir = os.path.basename(os.path.normpath(folder))
            zip_file.write(file, os.path.join(base_dir, filename))
        else:
            zip_file.write(file, os.path.join(custom_name, filename))


def _add_file_to_zipfile(zip_file, file, custom_name=None):
    if not custom_name:
        zip_file.write(file, os.path.basename(file))
    else:
        zip_file.write(file, custom_name)
