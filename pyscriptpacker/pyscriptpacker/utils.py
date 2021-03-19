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
        split_name = module['name'].split('.')
        if len(split_name) > 1:
            package_name = '.'.join(split_name[:-1])
        else:
            package_name = split_name[0]
        local_name = split_name[-1]
        setattr(sys.modules[package_name], local_name, sys.modules[module['name']])

for module in _modules:
    exec(module['code'], sys.modules[module['name']].__dict__)
'''


def get_setup_code():
    return setup_code
