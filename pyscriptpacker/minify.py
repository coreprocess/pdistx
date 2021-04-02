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
        self.obf_classes = False
        self.obf_functions = False
        self.obf_variables = True
        self.obf_import_methods = True
        self.obf_builtins = False


def minify(source, module, generator=None, table=None, obfuscate_src=True):
    config = MinifyConfig()

    tokens = token_utils.listified_tokenizer(source)
    source = minification.minify(tokens, config)
    # Have to re-tokenize for obfucation
    tokens = token_utils.listified_tokenizer(source)
    # Perform obfuscation if the related option were set
    if obfuscate_src:
        obfuscate.obfuscate(
            module,
            tokens,
            config,
            name_generator=generator,
            table=table,
        )

    # Convert back to text
    result = token_utils.untokenize(tokens)

    return result
