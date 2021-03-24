import os
import bz2
import base64


class FileHandler(object):
    '''
    A file handler class for getting all the content from a file.
    '''

    @classmethod
    def get_file_content(cls, file_name, file_path, compress=True):
        '''
        Get the content of given file with options for compressing the source.

        Args:
            file_name (string): The file for getting the content.
            file_path (string): The path to the file.
            compress (bool, optional): Whether the source will be compressed
                using bz2. Defaults to True.

        Returns:
            string: The whole content of the given file.
        '''
        content = ''
        with open(os.path.join(file_path, file_name), 'r') as file_data:
            content = file_data.read()

            if compress:
                # Reference: https://github.com/liftoff/pyminifier/blob/087ea7b0c8c964f1f907c3f350f5ce281798db86/pyminifier/compression.py#L51-L76
                compressed_source = bz2.compress(content.encode('utf-8'))
                content = 'import bz2, base64\n'
                content += 'exec(bz2.decompress(base64.b64decode("'
                content += base64.b64encode(compressed_source).decode('utf-8')
                content += '")))\n'
        return content
