import importlib
import types

# We use __import__ without any context information on purpose.
# The loader of the packer needs to be smart enough to handle this.
lib1 = __import__('lib1.mod1')
assert isinstance(lib1, types.ModuleType)
assert lib1.uid == '3ab2543e-9805-4b64-bb47-568367ab0fc9'
