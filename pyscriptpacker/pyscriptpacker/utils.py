setup_code = '''
import sys
import imp

for module in _modules:
    package_name = module['name'] if module['is_package'] else '.'.join(module['name'].split('.')[:-1])
    sys.modules[module['name']] = imp.new_module(module['name'])
    sys.modules[module['name']].__name__ = module['name']
    sys.modules[module['name']].__package__ = package_name
    if module['is_package']:
        sys.modules[module['name']].__path__ = []

for module in _modules:
    if not module['is_package']:
        package_name = '.'.join(module['name'].split('.')[:-1])
        local_name = module['name'].split('.')[-1]
        setattr(sys.modules[package_name], local_name, sys.modules[module['name']])

for module in _modules:
    exec(module['code'], sys.modules[module['name']].__dict__)
'''


def get_setup_code():
    return setup_code


def find_word_at(string, index):
    return string[:index].split(' ')[-1] + string[index:].split(' ')[0]
