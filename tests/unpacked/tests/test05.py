print('test05')

assert globals().get('mod1', None) is None

from lib1 import mod1
assert mod1 == 'not_a_module'
