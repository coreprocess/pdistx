@ECHO off

REM Current directory
pushd %~dp0

REM Install pyscriptpacker
pip install --upgrade pyscriptpacker

REM Pack libraries
mkdir .\\packed\\addon
python -m pyscriptpacker -z packed/addon.zip -m ./unpacked/__init__.py addon ./unpacked ./example_addon/__init__.py

popd
