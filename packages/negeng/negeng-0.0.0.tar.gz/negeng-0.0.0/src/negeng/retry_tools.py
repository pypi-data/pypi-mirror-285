import time

def simple_retry(func, count: int = 3, sec: int = None, *args, **kwargs):
    """Retry a function until it returns a truthy value.

    :param func: The function to call.
    :param args: Positional arguments to pass to the function.
    :param kwargs: Keyword arguments to pass to the function.
    :return: The return value of the function.
    """
    def _retry():
        return func(*args, **kwargs)
    
    for _ in range(count):
        try:
            return _retry()
        except Exception as e:
            if time:
                time.sleep(sec)
            continue