print('test03')

import types

assert globals().get('lib1', None) is None

import lib1.pak1

assert isinstance(lib1, types.ModuleType)
assert lib1.uid == '3ab2543e-9805-4b64-bb47-568367ab0fc9'
assert lib1.mod1 == 'not_a_module'

assert isinstance(lib1.pak1, types.ModuleType)
assert lib1.pak1.uid == 'ddc59226-69d5-40fe-9d75-cb7583b83bb1'

assert hasattr(lib1.pak1, 'mod2') == False
import lib1.pak1.mod2
assert hasattr(lib1.pak1, 'mod2') == True
