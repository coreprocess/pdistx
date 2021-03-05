from setuptools import setup, find_packages

import pyscriptpacker

setup(
    name='pyscriptpacker',
    version=pyscriptpacker.__version__,
    author=pyscriptpacker.__author__,
    license=pyscriptpacker.__license__,
    description=pyscriptpacker.__doc__.strip(),
    url=pyscriptpacker.__contact__,
    packages=find_packages(),
    install_requires=['toposort == 1.6'],
)
