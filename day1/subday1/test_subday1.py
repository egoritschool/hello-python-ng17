import pytest


@pytest.mark.parametrize(
    'param',
    ['val1', 'val2', 'val3']
)
def test_ok(param):
    pass

def test_nook():
    raise Exception