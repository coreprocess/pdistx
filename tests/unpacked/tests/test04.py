print('test04')

assert globals().get('lib1', None) is None

mod1 = '912dbd6f-95f1-4096-ad18-1f96b625ec7a'
import lib1.mod1
assert mod1 == '912dbd6f-95f1-4096-ad18-1f96b625ec7a'
