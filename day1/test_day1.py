import pytest
import task1


# @pytest.mark.skipif(not_changed('day1/task1.py'), reason='not updated')
def test_task1():
    with pytest.raises(ValueError):
        task1.method()

def test_true():
    pass


def test_overall():
    from day1 import script
    print('Output from the test')
    with pytest.raises(ValueError):
        script.method()


def test_day2():
    from day2 import script
    print('Output from the test')
    with pytest.raises(ValueError):
        script.method()
