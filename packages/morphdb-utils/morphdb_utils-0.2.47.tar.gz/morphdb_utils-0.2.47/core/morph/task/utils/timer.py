import signal
import time
from functools import wraps


def timetracker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        process_time = time.time() - start
        print(f"{func.__name__} took {process_time} seconds")
        return result

    return wrapper


class TimeoutException(Exception):
    def __init__(self, message):
        super().__init__(message)


def run_with_timeout(func, seconds, args=(), kwargs={}):
    def _handle_timeout(signum, frame):
        raise TimeoutException("Function call timed out")

    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.alarm(seconds)
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        raise e
    finally:
        signal.alarm(0)

    return result
