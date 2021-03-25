print('test01')

import types

assert globals().get('lib1', None) is None

import lib1

assert isinstance(lib1, types.ModuleType)
assert lib1.uid == '3ab2543e-9805-4b64-bb47-568367ab0fc9'
assert lib1.mod1 == 'not_a_module'
assert lib1.pak1 == 'not_a_package'
