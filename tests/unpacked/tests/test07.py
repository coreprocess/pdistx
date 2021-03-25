print('test07')

assert globals().get('uid', None) is None

from lib1.mod1 import uid
assert uid == 'a702559b-ca34-497a-8903-4e28d7eca849'
