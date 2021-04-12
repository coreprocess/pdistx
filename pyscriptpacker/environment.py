import os
import sys
import shutil
import tempfile
import subprocess
import virtualenv


class VirtualEnvironment(object):
    '''
    Class used for easy management the installed packages inside the virtual
    environment using the virtualenv package.
    '''

    def __init__(self, python_path=None):
        # setup virtual environment
        self._venv = tempfile.mkdtemp()
        virtualenv.cli_run([
            self._venv,
            '-p',
            python_path if python_path else sys.executable,
        ])
        # determin bin path
        if sys.platform == 'win32':
            self._bin = os.path.join(self._venv, 'Scripts')
        else:
            self._bin = os.path.join(self._venv, 'bin')
        # determine site-packages path
        self._site_packages = subprocess.check_output(
            ['python', '-c', 'import site; print(site.getsitepackages()[0])'],
            env={
                'PATH': self._bin + os.pathsep + os.environ['PATH'],
                'VIRTUAL_ENV': self._venv,
            },
        ).decode('utf-8').strip()
        if not self._site_packages:
            raise ValueError('Could not determine site-packages')

    def cleanup(self):
        '''
        Clean up the virtual environment folder.
        '''
        shutil.rmtree(self._venv)

    def get_site_packages_path(self):
        return self._site_packages

    def install_packages(self, packages):
        '''
        Install the packages into the virtual environment.

        Args:
            packages (list of string): The desired packages to be installed.
        '''
        subprocess.check_call(
            ['python', '-m', 'pip', 'install'] + packages,
            env={
                'PATH': self._bin + os.pathsep + os.environ['PATH'],
                'VIRTUAL_ENV': self._venv,
            },
        )
