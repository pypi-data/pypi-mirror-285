from src import gone


@gone.args
def no_args1(*args: None):
    assert not args
    return "with return"


@gone.args
def no_args2():
    return "with return"


@gone.result
def no_return(*args: int):
    assert args
    return "without return"


@gone.inout
def no_inout(*args: None):
    assert not args
    return "without return"


def test_args():
    assert no_args1(1, 2, "3")
    assert no_args2(1, 2, "3")


def test_return():
    assert no_return(1, 2, "3") is None


def test_both():
    assert no_inout(1, 2, "3") is None
