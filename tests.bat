@ECHO off

call ./tests/pack.bat

REM pytest
pip install --upgrade pytest
pytest tests

