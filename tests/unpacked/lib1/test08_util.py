assert globals().get('lib2', None) is None

import lib2
assert lib2.uid == 'bb7233ec-bda1-4f29-b728-406bdeb37110'
