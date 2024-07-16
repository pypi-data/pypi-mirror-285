import time
from typing import Callable, Optional, Any
from functools import wraps

def time_func(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, _no_time: Optional[bool] = False, **kwargs) -> float | Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        dt = end - start
        if _no_time:
            return result
        return dt
    return wrapper