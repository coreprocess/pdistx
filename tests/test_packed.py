import pytest
import sys, os.path

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'packed'))


@pytest.mark.forked
@pytest.mark.parametrize('test_case',
                         [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
def test_packed(test_case):
    import libs
    from libs.tests import run_test
    run_test(test_case)
    print('completed')
