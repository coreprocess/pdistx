import os
import sys
import shutil
import tempfile
import subprocess

try:
    import virtualenv
    HAS_VIRTUALENV = True
except ImportError:
    HAS_VIRTUALENV = False


class VirtualEnvironment(object):
    '''
    Class used for easy management the installed packages inside the virtual
    environment using the virtualenv package.
    '''

    def __init__(self, python_path=None):
        assert HAS_VIRTUALENV, 'virtualenv required'
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
        env = os.environ.copy()
        env.update({
            'PATH': self._bin + os.pathsep + os.environ['PATH'],
            'VIRTUAL_ENV': self._venv,
        })
        self._site_packages = subprocess.check_output(
            [
                os.path.join(self._bin, 'python'), '-c',
                'import os; import site; print(list(filter(lambda x: os.path.basename(x) == \'site-packages\', site.getsitepackages()))[0])'
            ],
            env=env,
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
        env = os.environ.copy()
        env.update({
            'PATH': self._bin + os.pathsep + os.environ['PATH'],
            'VIRTUAL_ENV': self._venv,
        })
        subprocess.check_call(
            [os.path.join(self._bin, 'python'), '-m', 'pip', 'install'] +
            packages,
            env=env,
        )