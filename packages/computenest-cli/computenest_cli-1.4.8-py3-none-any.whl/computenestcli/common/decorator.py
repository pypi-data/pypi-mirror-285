import time
from functools import wraps


def retry_on_exception(max_retries=5, delay=1, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal delay
            for attempt in range(max_retries - 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Retrying {func.__name__} due to {e}, attempt {attempt + 2} of {max_retries}...")
                    time.sleep(delay)
                    delay *= backoff
            return func(*args, **kwargs)

        return wrapper

    return decorator

