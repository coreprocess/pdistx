import os
import sys
import shutil
import tempfile
import subprocess


class VirtualEnvironment(object):
    '''
    Class used for easy management the installed packages inside the virtual
    environment using the virtualenv package.
    '''

    def __init__(self, python_path=None):
        try:
            import virtualenv
        except ImportError:
            self._install_packages(['virtualenv'])
            import virtualenv

        # Create the virtual environment in a temporary directory
        self._temp = tempfile.mkdtemp()
        virtualenv.cli_run([
            self._temp,
            '-p',
            sys.executable if python_path is None else python_path,
        ])
        if sys.platform == 'win32':
            self._vpython_path = os.path.join(self._temp, 'Scripts', 'python')
            self._vsite_path = os.path.join(self._temp, 'Lib', 'site_packages')
        else:
            version = os.listdir(os.path.join(self._temp, 'lib'))[0]
            self._vpython_path = os.path.join(self._temp, 'bin', 'python')
            self._vsite_path = os.path.join(
                self._temp,
                'lib',
                version,
                'site-packages',
            )

    def __del__(self):
        '''
        Clean up the virtual environment folder.
        '''
        shutil.rmtree(self._temp)

    def get_site_packages_path(self):
        return self._vsite_path

    def install_packages(self, packages):
        '''
        Install the packages into the virtual environment.

        Args:
            packages (list of string): The desired packages to be installed.
        '''
        self._install_packages(packages, self._vpython_path)

    def _install_packages(self, packages, python_path=None):
        '''
        Install the packages using python command line.

        Args:
            packages (list of string): The desired packages to be installed.
            python_path (string): The python executable path.
        '''
        subprocess.check_call([
            'python' if python_path is None else python_path,
            '-m',
            'pip',
            'install',
            ','.join(packages),
        ])
