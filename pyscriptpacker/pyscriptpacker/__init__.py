"""
Convert Python packages into a single file.
"""

__author__ = '3DNinjas Team'
__version__ = '0.0.1'
__license__ = 'TBD'  # Create and see LICENSE file.
__contact__ = 'https://github.com/3dninjas/pyscriptpacker2'
__status__ = 'In active development'

# TODO(Nghia Lam):
#   - [X] Loop through all the file codes in each modules.
#   - [X] Detect import dependencies.
#   - [X] Sort import order based on the dependencies graph (using toposort).
#   - [X] Scope root python name to avoid name clash.
#   - [ ] Change CLI to support a list module input from user.
#   - [ ] Output with Python 2/3 compatible.
#   - [ ] Documentation.
#   - [ ] IMPORTANT: Code quality improvement.
#   - [ ] IMPORTANT: Code quality review.
