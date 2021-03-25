@ECHO off

REM Project root
pushd %~dp0

pip install --upgrade virtualenv
virtualenv ./envs --prompt "envs"  
call ./envs/Scripts/activate.bat
python -m pip install --upgrade pip

call ./tests/pack.bat

REM pytest
pip install --upgrade pytest
python -m pytest tests -p no:warnings

popd
