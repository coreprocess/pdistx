@ECHO off

REM Current directory
pushd %~dp0

REM Install pyscriptpacker
pip install --upgrade pyscriptpacker

REM Pack libraries
python -m pyscriptpacker -c custom_widgets ./unpacked ./packed/my_lib.py

popd
