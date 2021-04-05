import os
import sys
import shutil
import subprocess


class VirtualEnvironment(object):
    '''
    Class used for easy management the installed packages inside the virtual
    environment using the virtualenv package.
    '''

    _VIRTUAL_ENV = 'pyscriptpacker_env'

    def __init__(self, python_path):
        try:
            import virtualenv
        except ImportError:
            self._install_packages(['virtualenv'], python_path)
            import virtualenv

        # Create the virtual environment
        virtualenv.cli_run([self._VIRTUAL_ENV])

    def __del__(self):
        '''
        Clean up the virtual environment folder.
        '''
        pass
        # shutil.rmtree(self._VIRTUAL_ENV)

    def get_site_packages_path(self):
        return os.path.join(self._VIRTUAL_ENV, 'Lib', 'site_packages')

    def install_packages(self, packages):
        '''
        Install the packages into the virtual environment.

        Args:
            packages (list of string): The desired packages to be installed.
        '''
        pass

    def _install_packages(self, packages, python_path=None):
        '''
        Install the packages using python command line.

        Args:
            packages (list of string): The desired packages to be installed.
            python_path (string): The python executable path.
        '''
        if python_path is None:
            python_path = sys.executable
        subprocess.check_call(
            [python_path, '-m', 'pip', 'install', ','.join(packages)])
