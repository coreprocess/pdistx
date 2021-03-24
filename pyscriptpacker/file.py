import os
import bz2
import base64

from queue import Queue


class FileQueue(object):
    '''
    A simple file queue system.
    '''

    def __init__(self):
        self._files = Queue()
        self._roots = Queue()

    def put(self, file, root):
        self._files.put(file)
        self._roots.put(root)

    def get_file(self):
        return self._files.get()

    def get_root(self):
        return self._roots.get()

    def empty(self):
        return self._files.empty()

    def in_queue(self, file, root):
        return file in self._files.queue and root in self._roots.queue


class FileHandler(object):
    '''
    A file handler class for getting all the content from a file.
    '''

    @classmethod
    def get_file_content(cls, file_name, file_path, compress=True):
        '''
        Get the content of the given file with options for compressing the
        source and rewrite the import into relative scope.

        Args:
            file_name (string): The file for getting the content.
            file_path (string): The path to the file.
            module_name (string): The module name content the file.
            target_names (string): All the target module name for rewriting.
            compress (bool, optional): Whether the source will be compressed
                using bz2. Defaults to True.
            rewrite_import (bool, optional): Whether the imports will be
                rewritten to relative scope. Defaults to True.

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
