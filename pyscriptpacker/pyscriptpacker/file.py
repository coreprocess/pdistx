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


class FileReader(object):
    '''
    A file reader class for getting all the content from a file.
    '''

    @classmethod
    def get_file_content(cls,
                         file_name,
                         file_path,
                         module_name,
                         target_names,
                         compress=True,
                         rewrite_import=True):
        content = ''
        with open(os.path.join(file_path, file_name), 'r') as file_data:
            content = file_data.readlines()
            if rewrite_import:
                cls._rewrite_to_relative_scope(
                    content,
                    module_name,
                    target_names,
                )
            content = ''.join(content)

            if compress:
                # Compress the source code using bz2
                # Reference: https://github.com/liftoff/pyminifier/blob/087ea7b0c8c964f1f907c3f350f5ce281798db86/pyminifier/compression.py#L51-L76
                compressed_source = bz2.compress(content.encode('utf-8'))
                content = 'import bz2, base64\n'
                content += 'exec(bz2.decompress(base64.b64decode("'
                content += base64.b64encode(compressed_source).decode('utf-8')
                content += '")))\n'
        return content

    @classmethod
    def _rewrite_to_relative_scope(cls, content, module, target_names):
        dot_lvl = 1
        dot_lvl += 1 if (module.count('.') == 0) else module.count('.')
        dot = '.' * dot_lvl

        for line in content:
            if 'import' in line:
                # Find indentation
                indent = ''
                for char in line:
                    if char == ' ':
                        indent += char
                    else:
                        break
                # Parsing throught line
                splits = line.split()
                for name in target_names:
                    for word in splits:
                        scope = word
                        if '.' in word:
                            scope = word.split('.')[0]  # Get the highest scope
                        if name == scope:
                            if 'from' in line:
                                splits[splits.index(word)] = dot + word
                            else:
                                prefix = ''
                                suffix = word
                                if '.' in word:
                                    prefix = '.'.join(word.split('.')[:-1])
                                    suffix = word.split('.')[-1]
                                splits.insert(0, 'from')
                                splits.insert(1, dot + prefix)
                                splits[splits.index(word)] = suffix
                            break

                content[content.index(line)] = indent + ' '.join(splits) + '\n'
