import functools
import typing as t

P = t.ParamSpec("P")
R = t.TypeVar("R")


def args(fn: t.Callable[P, R]) -> t.Callable[..., R]:
    """
    A decorator that absorbs all input arguments and calls the decorated function without them.

    Args:
        fn (t.Callable[P, R]): The function to be decorated.

    Returns:
        t.Callable[..., R]: A decorated function that ignores its input arguments.
    """

    @functools.wraps(fn)
    def inner(*_: t.Any, **__: t.Any) -> R:
        return fn()

    return inner


def result(fn: t.Callable[P, R]) -> t.Callable[P, None]:
    """
    A decorator that discards the result of the decorated function.

    Args:
        fn (t.Callable[P, R]): The function to be decorated.

    Returns:
        t.Callable[P, None]: A decorated function that ignores its output.
    """

    @functools.wraps(fn)
    def inner(*a: P.args, **kw: P.kwargs) -> None:
        fn(*a, **kw)
        return None

    return inner


def inout(fn: t.Callable[P, R]) -> t.Callable[..., None]:
    """
    A decorator that absorbs all input arguments and discards the result of the decorated function.

    Args:
        fn (t.Callable[P, R]): The function to be decorated.

    Returns:
        t.Callable[..., None]: A decorated function that ignores both its input and output.
    """

    @functools.wraps(fn)
    def inner(*_: t.Any, **__: t.Any) -> None:
        fn()
        return None

    return inner
