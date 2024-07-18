import time
import functools
from typing import Callable


def simple_retry(count: int = 3, sec: int = None, *args, **kwargs) -> Callable:
    """Retry a function until it returns a truthy value.

    :param func: The function to call.
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    :return: The return value of the function.
    """
    def dec_retry(func):
        @functools.wraps(func)
        def inner_function(*args, **kwargs):
            for _ in range(count):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if sec is not None:
                        time.sleep(sec)
        return inner_function

    return dec_retry