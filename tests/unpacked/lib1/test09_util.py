assert globals().get('lib2', None) is None

mod3 = '29ac8fa3-da86-4334-aa4b-809b29b41fdd'

import lib2.mod3

assert lib2.mod3.uid == '117839d0-ba0d-45db-8bfe-49c193ca862e'
assert mod3 == '29ac8fa3-da86-4334-aa4b-809b29b41fdd'
