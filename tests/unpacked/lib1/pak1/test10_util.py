import importlib
import types

assert isinstance(importlib, types.ModuleType)

x = '..mod1'
mod1 = importlib.import_module(x, __package__)
assert isinstance(mod1, types.ModuleType)
assert mod1.uid == 'a702559b-ca34-497a-8903-4e28d7eca849'
