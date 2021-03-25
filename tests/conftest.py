import sys
import pytest

initial_modules = list(sys.modules.keys())


@pytest.fixture
def init_modules():
    return initial_modules
