import time
from functools import wraps

def retry_decorator(max_retries=3, delay=1):
    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed: {e}, retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"Attempt {attempt + 1} failed: {e}, no more retries.")
                        raise
        return wrapper
    return decorator_retry