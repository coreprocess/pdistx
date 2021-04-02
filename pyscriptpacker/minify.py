from pyminifier import minification
from pyminifier import token_utils
from pyminifier import obfuscate


class MinifyConfig(object):
    '''
    Default configuration for the wrapper of the pyminifier plugins, this
    configs is mapping 1:1 with the options of the pyminifier.
    '''

    def __init__(self):
        self.replacement_length = 1
        self.tabs = False
        self.use_nonlatin = False
        self.obfuscate = False
        self.obf_classes = False  # pyminifier bug: cause trouble when import between files.
        self.obf_functions = False  # pyminifier bug: wrong rename when relative import.
        self.obf_variables = True
        self.obf_import_methods = True
        self.obf_builtins = False  # pyminifier bug: wrong indent on super short file.


class MinifyManager(object):
    '''
    A wrapper of pyminifier plugin, we mainly for minify and obfuscate the
    source when packing.
    '''

    def __init__(self, obfuscate_src):
        self._obfuscate_src = obfuscate_src

        self._config = MinifyConfig()
        self._generator = obfuscate.obfuscation_machine(
            identifier_length=self._config.replacement_length)
        self._table = [{}]

    def minify(self, source, module):
        tokens = token_utils.listified_tokenizer(source)
        source = minification.minify(tokens, self._config)
        # Have to re-tokenize for obfucation
        tokens = token_utils.listified_tokenizer(source)
        # Perform obfuscation if the related option were set
        if self._obfuscate_src:
            obfuscate.obfuscate(
                module,
                tokens,
                self._config,
                name_generator=self._generator,
                table=self._table,
            )

        # Convert back to text
        result = token_utils.untokenize(tokens)

        return result
