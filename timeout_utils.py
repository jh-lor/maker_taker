import _thread
import threading
from contextlib import contextmanager


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds, msg=''):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException()
    finally:
        # if the action ends in specified time, timer is canceled
        timer.cancel()


def run_function_with_time_limit(func, *args, timer=1, msg=''):
    try:
        with time_limit(timer):
            return func(*args)
    except TimeoutException as e:
        print("Timed Out:", msg)
    except Exception as e:
        print(e)
    return None
