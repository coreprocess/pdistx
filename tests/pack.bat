@ECHO off

REM Current directory
pushd %~dp0

REM Install current dev packer
pip install --upgrade ../

REM Pack libraries
mkdir .\\packed\\libs
python -m pyscriptpacker -c tests,lib1,lib2,lib3 ./unpacked ./packed/libs/__init__.py

popd
