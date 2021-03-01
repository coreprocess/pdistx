from setuptools import setup, find_packages

import pyscriptpacker

setup(
    name='pyscriptpacker',
    version=pyscriptpacker.__version__,
    author=pyscriptpacker.__author__,
    license=pyscriptpacker.__license__,
    description='Convert Python packages into a single file.',
    url='https://github.com/3dninjas/pyscriptpacker2',
    packages=find_packages(),
    install_requires=[],
)
