@ECHO off

call ./tests/pack.bat

REM Pytest installation
pip install --upgrade pytest

REM Running test cases
pytest tests

