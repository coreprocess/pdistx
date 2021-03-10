py2_setup_code = '''
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
    exec module['code'] in sys.modules[module['name']].__dict__
'''

py3_setup_code = '''
import importlib.util

for module in _modules:
    sys.modules[module['name']] = importlib.util.module_from_spec(
        importlib.util.spec_from_loader(module['name'],
                                        loader=None,
                                        is_package=str(module['is_package'])))

for module in _modules:
    if not module['is_package']:
        package_name = '.'.join(module['name'].split('.')[:-1])
        local_name = module['name'].split('.')[-1]
        setattr(sys.modules[package_name], local_name, sys.modules[module['name']])

for module in _modules:
    exec(module['code'], sys.modules[module['name']].__dict__)
'''


def find_word_at(string, index):
    return string[:index].split(' ')[-1] + string[index:].split(' ')[0]
