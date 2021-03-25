import pytest
import sys, os.path
sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'unpacked'))


@pytest.mark.parametrize('test_case', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
def test_packed(test_case, init_modules):
    # Second or subsequent run: remove all but initially loaded modules
    for m in list(sys.modules):
        if m not in init_modules:
            del sys.modules[m]

    import libs
    from libs.tests import run_test
    run_test(test_case)
