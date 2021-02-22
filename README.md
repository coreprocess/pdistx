# Python Template

```sh
# Install formatter and linter packages
pip install yapf
pip install pylint
```

# Python Interpreter

## Python 2.7 on Ubuntu 20.04 LTS

```sh
# install python 2.7
sudo apt install python2
# install pip for python 2.7
sudo apt install curl
curl https://bootstrap.pypa.io/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
# validate versions
python2 --version
pip --version
# configure virtual environment
sudo pip install virtualenv
virtualenv -p /bin/python2 env2
source ./env2/bin/activate
```

# Virtual Environment

## Python 3.x

1. Setup a new environment: `python3 -m venv env3` (make sure to run python 3.x)
2. Activate environment: `source ./env3/bin/activate` on Unix and `source ./env3/Scripts/activate` (Bash) or `env3\Scripts\activate.bat` (Cmd/PowerShell) on Windows
3. Update pip: `python -m pip install --upgrade pip`
4. Install lib1 library: `pip install -e lib1`
5. Install lib2 library: `pip install -e lib2`
6. Run example: `python -m template_lib2`
7. Deactivate the environment: `deactivate`

## Python 2.7

1. Setup a new environment: `pip install virtualenv && virtualenv -p /usr/bin/python env2` (make sure the path is pointing to Python 2.7 on your system)
2. Activate environment: `source ./env2/bin/activate` on Unix and `source ./env2/Scripts/activate` (Bash) or `env2\Scripts\activate.bat` (Cmd/PowerShell) on Windows
3. Update pip: `python -m pip install --upgrade pip`
4. Install lib1 library: `pip install -e lib1`
5. Install lib2 library: `pip install -e lib2`
6. Run example: `python -m template_lib2`
7. Deactivate the environment: `deactivate`
