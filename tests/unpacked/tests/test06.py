print('test06')

import types

import lib1.mod1
from lib1 import mod1
assert isinstance(mod1, types.ModuleType)
assert mod1.uid == 'a702559b-ca34-497a-8903-4e28d7eca849'
