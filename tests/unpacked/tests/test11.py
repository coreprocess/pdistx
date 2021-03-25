print('test11')

import types

assert globals().get('auto1', None) is None
assert globals().get('auto2', None) is None

from lib3 import *
assert isinstance(auto1, types.ModuleType)
assert auto1.uid == '49db6347-32a7-4405-996e-ee7c2b493e61'
assert isinstance(auto2, types.ModuleType)
assert auto2.uid == 'ef171e2e-f3ef-460f-934d-c30041b4dad2'
